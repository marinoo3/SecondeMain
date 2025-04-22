from flask import Flask, session, request, render_template, jsonify
from markupsafe import escape
from functools import wraps
import os

from custom import Shopify, Klaviyo, Products



# APP LOGIC


app = Flask(__name__)
app.secret_key = os.environ['SECRET_KEY']

def check_api_key(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'authenticated' in session:
            return f(*args, **kwargs)
        
        api_key = request.args.get('apikey')
        
        if api_key and api_key == app.secret_key:
            session['authenticated'] = True
            return f(*args, **kwargs)
        
        return jsonify({"message": "Unauthorized"}), 401
        
    return wrapper

def fix_attributes(attrs):

    if not 'name' in attrs:
        attrs['name'] = 'Matchy'
    if not 'lastName' in attrs:
        attrs['lastName'] = 'Cycling'
    if not 'email' in attrs:
        attrs['email'] = 'hello@matchycycling.com'
    if not 'phone' in attrs:
        attrs['phone'] = ""

    return attrs




# VIEWS ROUTES
    

@app.route('/')
@check_api_key
def index_main():
    return render_template('ajouter.html')

@app.route('/inventaire.html')
@check_api_key
def index_inventaire():
    return render_template('inventaire.html')

@app.route('/ajouter.html')
@check_api_key
def index_ajouter():
    return render_template('ajouter.html')




# API ROUTES


@app.route('/search_customer/<email>', methods=['GET'])
@check_api_key
def search_customer(email):

    email = escape(email)
    customer = SHOPIFY.get_customer(email)

    exists = False
    if customer:
        exists = True
    
    return jsonify({'exists': exists})

@app.route('/ajouter', methods=['POST'])
@check_api_key
def add_item():

    attributes = fix_attributes(request.get_json())
    id, title = INVENTAIRE.save_product(attrs=attributes)

    response = {
        'status': 200,
        'data': {
            'id': id,
            'product_title': title
        }
    }

    return response

@app.route('/load_products/<ft>', methods=['GET'])
@check_api_key
def load_products(ft):

    products = INVENTAIRE.load_products(location=ft)
    products_json = [ p.condense_json() for p in products ]

    return jsonify({'products': products_json})

@app.route('/search_products/<query>', methods=['GET'])
@check_api_key
def search_products(query):

    query = escape(query)

    products = []
    for p in INVENTAIRE.filter_products(query):

        if not p:
            continue

        products.append(p.condense_json())

    return jsonify({'products': products})

@app.route('/get_giftcard_info/<id>', methods=['GET'])
@check_api_key
def get_giftcard_info(id):

    giftcard_content = SHOPIFY.get_gift_card(id)
    return jsonify({'giftcard': giftcard_content})

@app.route('/preview_product/<id>', methods=['GET'])
@check_api_key
def preview_product(id):

    p = INVENTAIRE.get_by_id(id)
    print('product id:', id)
    return jsonify({'product': p.complete_json()})

@app.route('/sell_product/<id>', methods=['POST'])
@check_api_key
def sell_product(id:str):

    p = INVENTAIRE.get_by_id(id) # get product

    gift_card_id = None
    if p.seller['email'] != 'hello@matchycycling.com':

        gift_card = SHOPIFY.create_gift_card(p.seller['email'], p.product['secondhandPrice'], p.id)
        gift_card_id = gift_card.id

    email_data = {
            'name': p.seller['name'],
            'email': p.seller['email'],
            'item_title': p.compressed_title,
            'value': p.product['secondhandPrice'],
            'item_code': p.id
        }
    KLAVIYO.send_email(email_data)

    INVENTAIRE.remove_product(id, gift_card_id)

    return jsonify({'status': 'success', 'data': {'seller': p.seller['name']}})


# INIT
    

INVENTAIRE = Products.Inventaire()
SHOPIFY = Shopify.ShopifyManager()
KLAVIYO = Klaviyo.KlaviyoManager()
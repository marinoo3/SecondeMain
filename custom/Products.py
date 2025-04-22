from flask import url_for
from datetime import date

from . import db

from typing import Optional



class Product():

    def __init__(self, attrs: dict, loc='inventory') -> None:

        self.id = attrs['id']
        self.location = loc
        self.seller = self.__seller(attrs)
        self.product = self.__product(attrs)
        self.img_src = self.__icon_from_type(attrs['productType'])
        self.giftcard_id = attrs.get('giftCardID', None)
        self.title = f"{attrs['productType'].replace('-', ' ').capitalize()} {attrs['gamme'].capitalize()} - {attrs['color'].capitalize()}"
        self.compressed_title = f"{attrs['productType'].replace('-', ' ').capitalize()} {attrs['gamme'].capitalize()} {attrs['color'].capitalize()} - {attrs['size'].upper()}"
        self.size = f"{attrs['gender'].capitalize()} - {attrs['size'].upper()}"


    def __icon_from_type(self, type: str) -> str:

        if type == 'maillot':
            return url_for('static', filename='images/icon-maillot.svg')
        elif type in ['veste-hiver', 'veste-mi-saison', 'gilet', 'bomber']:
            return url_for('static', filename='images/icon-veste.svg')
        elif type in ['cuissard', 'collant']:
            return url_for('static', filename='images/icon-cuissard.svg')
        elif type in ['gravel-tee', 't-shirt']:
            return url_for('static', filename='images/icon-tee.svg')
        else:
            return url_for('static', filename='images/icon-accessoires.svg')
        

    def __seller(self, attrs: dict) -> dict:

        seller = {
            'name': attrs['name'].capitalize(),
            'lastName': attrs['lastName'].capitalize(),
            'email': attrs['email'].lower(),
            'phone': attrs['phone']
        }

        return seller
    
    
    def __product(self, attrs: dict) -> dict:

        product = {
            'productType': attrs['productType'],
            'gamme': attrs['gamme'],
            'gender': attrs['gender'],
            'size': attrs['size'],
            'color': attrs['color'],
            'collection': attrs['collection'],
            'etat': attrs['etat'],
            'originalPrice': attrs['originalPrice'],
            'secondhandPrice': attrs['secondhandPrice']
        }

        return product
    
    
    def formated_id(self) -> str:

        return "{:04d}".format(self.id)
    
    
    def condense_json(self) -> dict:

        p_json = {
            'id': self.formated_id(),
            'img_src': self.img_src,
            'title': self.title,
            'size': self.size,
            'seller': self.seller
        }
        return p_json
    

    def complete_json(self) -> dict:

        p_json = {
            'location': self.location,
            'img_src': self.img_src,
            'title': self.title,
            'size': self.size,
            'originalPrice': self.product['originalPrice'],
            'secondhandPrice': self.product['secondhandPrice'],
            'sellerName': self.seller['name'],
            'sellerLastName': self.seller['lastName'],
            'sellerEmail': self.seller['email'],
            'sellerPhone': self.seller['phone'],
            'discountID': self.giftcard_id
        }

        return p_json



class Inventaire():

    def __init__(self) -> None:

        self.products = []
        self.database = db.Database()


    def load_products(self, location='inventory') -> Optional[list]:

        # empty products list
        self.products = []

        products_attrs = self.database.get_products(location=location)
        for p_attrs in products_attrs:
            product = Product(p_attrs, loc=location)
            self.products.append(product)

        return self.products
    
    
    def filter_products(self, query:str) -> list:

        if len(query) == 4:

            try:
                int(query) # if the query is a product ID
                return [self.get_by_id(query)]
            except ValueError:
                pass

        # else check for match
        filtered_products = []
        for p in self.products:

            # query match with product title?
            if query.lower() in p.title.lower():
                filtered_products.append(p)

            # query match with owner name?
            elif query.lower() in p.seller['name'].lower():
                filtered_products.append(p)

            # query match with owner last name?
            elif query.lower() in p.seller['lastName'].lower():
                filtered_products.append(p)

            # query matchy with product price?
            elif query in [p.product['originalPrice'], p.product['secondhandPrice']]:
                filtered_products.append(p)

        return filtered_products
    

    def save_product(self, attrs: dict) -> [str, str]:

        attrs['location'] = 'inventory'
        attrs['enterDate'] = date.today()
        if 'checkbox' in attrs.keys():
            attrs.pop('checkbox')

        id = self.database.add_product(attrs)

        attrs['id'] = id
        p = Product(attrs, loc=attrs['location'])

        return p.formated_id(), p.title


    def remove_product(self, id:str, gift_card_id:str) -> None:

        new_values = {
            "location": "history",
            "giftCardID": gift_card_id,
            "soldDate": date.today()
        }

        id = int(id)
        self.database.move_product(id, new_values)


    def get_by_id(self, id: str) -> Optional[Product]:

        id = int(id) # tansform str to int

        if self.products == []:
            self.load_products()

        for p in self.products:
            if p.id == id:
                return p
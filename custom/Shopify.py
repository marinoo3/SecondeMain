import shopify
import os

from typing import Optional
from pyactiveresource.connection import ResourceNotFound



class ShopifyManager():

    def __init__(self) -> None:
        self.access_token = os.environ['SHOPIFY_ACCESS_TOKEN']
        self.shop_url = 'matchycycling.myshopify.com'
    
    def get_customer(self, email:str) -> Optional[str]:

        with shopify.Session.temp(self.shop_url, '2023-01', self.access_token):

            response = shopify.Customer.search(query=email)

            if response == []:
                return None
            else:
                customer = response[0]
                return customer
        
    def create_customer(self, fn:str, ln:str, email:str) -> None:

        with shopify.Session.temp(self.shop_url, '2023-01', self.access_token):

            new_customer = shopify.Customer()
            new_customer.first_name = fn
            new_customer.last_name = ln
            new_customer.email = email
            new_customer.tags = "Seconde main"
            success = new_customer.save()

            if not success:
                raise Exception(f'Impossible to create {email}')
            
    def create_gift_card(self, email:str, amount:float, product_id:int) -> shopify.GiftCard:

        customer = self.get_customer(email)

        with shopify.Session.temp(self.shop_url, '2023-01', self.access_token):
        
            gift_card = shopify.GiftCard.create({
                'customer_id': customer.id,
                'initial_value': str(amount),
                'note': f'Vente seconde main #{product_id}'
            })

        return gift_card
    
    def get_gift_card(self, id:str) -> dict:

        with shopify.Session.temp(self.shop_url, '2023-01', self.access_token):

            try:

                gift_card = shopify.GiftCard.find(id_=id)

                if gift_card:

                    content = {
                        'id': id,
                        'code': "•••• •••• •••• " + gift_card.last_characters,
                        'initialValue': gift_card.initial_value,
                        'balance': gift_card.balance
                    }

            except ResourceNotFound:

                print('no gift card found, returning dummy output')

                content = {
                    'id': id,
                    'code': id,
                    'initialValue': "",
                    'balance': ""
                }

        return content
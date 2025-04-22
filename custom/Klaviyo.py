import requests
import os



class KlaviyoManager():
    
    def __init__(self) -> None:
        self.api_key = os.environ['KLAVIYO_API_KEY']
        

    def send_email(self, email_data:dict) -> None:

        url = "https://a.klaviyo.com/api/events/"

        payload = { 
            "data": {
                "type": "event",
                "attributes": {
                    "properties": {
                        "value": str(email_data['value']),
                        "item_title": email_data['item_title'],
                        "item_code": email_data['item_code']
                    },
                    "value": str(email_data['value']),
                    "metric": { 
                        "data": {
                            "type": "metric",
                            "attributes": { "name": "Vente seconde main" }
                        } 
                    },
                    "profile": { 
                        "data": {
                            "type": "profile",
                            "attributes": {
                                "email": email_data['email'],
                                "first_name": email_data['name']
                            }
                        } 
                    }
                }
            } 
        }

        headers = {
            "accept": "application/json",
            "revision": "2024-02-15",
            "content-type": "application/json",
            "Authorization": f"Klaviyo-API-Key {self.api_key}"
        }

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code != 202:
            print(response.text)
            raise Exception("Failed to trigger Klaviyo flow; the email hasn't been sent!")

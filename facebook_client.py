import json
from datetime import datetime
import os
from datastore import Datastore
from dotenv import load_dotenv
import httpx


datastore = Datastore()
load_dotenv()
class FacebookClient:

    def __init__(self):
        self.API_URL = "https://graph.facebook.com/v2.6/me/messages"
        self.PARAMS = {"access_token": os.environ.get("FACEBOOK_PAGE_TOKEN")}
        self.HEADERS = {"Content-Type": "application/json"}
       
    def send_text_message(self,message, sender_id):
        response = httpx.post(
            self.API_URL,
            params=self.PARAMS,
            headers=self.HEADERS,
            json={
                "recipient": {"id": sender_id},
                "message": {"text": message},
                "messaging_type": "UPDATE",
            },
        )

        assert response.status_code == 200, "Error sending message"
        return response.status_code


    def process_msg(self, data):
    
        for entry in data.entry:
            messaging_events = [
                event for event in entry.get("messaging", []) if event.get("message")
            ]
            for event in messaging_events:
                response = {
                    "body": event.get("message").get("text"),
                    "sender_id":  event["sender"]["id"]
            }
            chat_details = {
                "sender": response["sender_id"],
                "incoming": True,
                "message_type": "text",
                "message": response["body"],
                "created_at": datetime.now(),
                "app_type": "whatsapp",
                "receiver":  data.entry["id"],
            }
            datastore.create(
                sender_id=response["sender_id"],
                details=chat_details,
                chat=True,
            )
            
           

        return {
            "statusCode": 403,
            "body": json.dumps("Unsupported method"),
            "isBase64Encoded": False
        }



if __name__ == "__main__":
    client = FacebookClient()
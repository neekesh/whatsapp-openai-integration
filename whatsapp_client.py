import os
import requests
import json

from dotenv import load_dotenv
load_dotenv()

class WhatsAppClient:

    API_URL = "https://graph.facebook.com/v18.0/"
    WHATSAPP_API_TOKEN = os.environ.get("WHATSAPP_API_TOKEN")
    WHATSAPP_CLOUD_NUMBER_ID = os.environ.get("WHATSAPP_CLOUD_NUMBER_ID")

    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {self.WHATSAPP_API_TOKEN}",
            "Content-Type": "application/json",
        }
        if self.WHATSAPP_CLOUD_NUMBER_ID is None:
            raise ValueError("Environment variable WHATSAPP_CLOUD_NUMBER_ID is not set.")
        else:
            self.API_URL = self.API_URL + self.WHATSAPP_CLOUD_NUMBER_ID

    def send_text_message(self,message, phone_number):
        payload = {
            "messaging_product": 'whatsapp',
            "to": phone_number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": message
            }
        }
        response = requests.post(f"{self.API_URL}/messages", json=payload,headers=self.headers)
        assert response.status_code == 200, "Error sending message"
        return response.status_code


    def process_notification(self, data):
        entries = data["entry"]
        for entry in entries:
            for change in entry["changes"]:
                value = change["value"]
                if value:
                    if "messages" in value:
                        for message in value["messages"]:
                            if message["type"] == "text":
                                from_no = message["from"]
                                message_body = message["text"]["body"]
                                prompt = message_body
                                return {
                                    "statusCode": 200,
                                    "body": prompt,
                                    "sender_id": from_no,
                                    "isBase64Encoded": False
                                }

        return {
            "statusCode": 403,
            "body": json.dumps("Unsupported method"),
            "isBase64Encoded": False
        }



if __name__ == "__main__":
    client = WhatsAppClient()
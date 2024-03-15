
import os
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks, status,Response
import logging
from whatsapp_client import WhatsAppClient
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from typing import List
from openai_client import OpenAIClient
from dotenv import load_dotenv
import httpx
from datetime import datetime

from datastore import Datastore

wtsapp_client = WhatsAppClient()
logger = logging.getLogger(__name__)
load_dotenv()
app = FastAPI()
datastore = Datastore()


# Request Models.
class WebhookRequestData(BaseModel):
    object: str = ""
    entry: List = []


@app.get("/webhook")
async def whatsapp_webhook_validation(request: Request):

    if request.query_params.get('hub.verify_token') == os.getenv("WHATSAPP_HOOK_TOKEN"):
        return int(request.query_params.get('hub.challenge'))
    else:
        raise HTTPException(status_code=400, detail="Failure")


def send_whatsapp_message(message, phone_number):
    response = wtsapp_client.send_text_message(message=message, phone_number=phone_number)
    if response == 200:
        chat_details = {
                    "sender": phone_number,
                    "incoming": False,
                    "message_type": "text",
                    "reciever": os.environ.get("WHATSAPP_CLOUD_NUMBER_ID"),
                    "message": message,
                    "created_at": datetime.now(),
                    "app_type": "whatsapp",
         }
        datastore.create(
            sender_id=phone_number,
            details=chat_details,
            chat=True,
        )      


def send_message(data, to):
    openai_client = OpenAIClient()
   
    sender_id = data["sender_id"]
    reply = openai_client.complete(question=data["body"], sender_id=sender_id )

    if to == "whatsapp":
        send_whatsapp_message(message=reply, phone_number=sender_id)
    else:
         
        response = httpx.post(
            "https://graph.facebook.com/v2.6/me/messages",
            params={"access_token": os.environ.get("FACEBOOK_PAGE_TOKEN")},
            headers={"Content-Type": "application/json"},
            json={
                "recipient": {"id": sender_id},
                "message": {"text": reply},
                "messaging_type": "UPDATE",
            },
        )
        # if response.status_code == 200:
        #     chat_details["app_type"] = "messenger"
        #     chat_details["receiver"] =  os.environ.get("WHATSAPP_CLOUD_NUMBER_ID")
        #     datastore.create_chats(
        #         sender_id=sender_id,
        #         details=chat_details
        #     )
        

@app.post("/webhook", status_code=status.HTTP_200_OK)
async def receive_msg(request: Request, background_task: BackgroundTasks):
    
    data = await request.json()
    response = wtsapp_client.process_notification(data)

    if response["statusCode"] == 200:
        if response["body"] and response["sender_id"]:

            chat_details = {
                    "sender": response["sender_id"],
                    "incoming": True,
                    "message_type": "text",
                    "message": response["body"],
                    "created_at": datetime.now(),
                    "app_type": "whatsapp",
                    "receiver":  os.environ.get("WHATSAPP_CLOUD_NUMBER_ID"),
                }
            datastore.create(
                sender_id=response["sender_id"],
                details=chat_details,
                chat=True,
            )
            background_task.add_task(send_message, response,"whatsapp")
            
    return jsonable_encoder({"status": "success"})




@app.get("/webhook/messenger")
async def messenger_webhook_validation(request: Request):
    if request.query_params.get("hub.mode") == "subscribe" and request.query_params.get(
        "hub.challenge"
    ):
        if (
            not request.query_params.get("hub.verify_token")
            == os.environ["MESSENGER_HOOK_TOKEN"]
        ):
            return Response(content="Verification token mismatch", status_code=403)
        return Response(content=request.query_params["hub.challenge"])

    return Response(content="Required arguments haven't passed.", status_code=400)


@app.post("/webhook/messenger")
async def messenger_webhook(data: WebhookRequestData, background_task: BackgroundTasks):
    """
    Messages handler.
    """
    if data.object == "page":
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
            
            background_task.add_task(send_message, response,"facebook")

    return jsonable_encoder({"status": "success"})


@app.get("/chats/{phone_no}")
async def get_thread_id(phone_no):
    return datastore.get_chats(phone_no)
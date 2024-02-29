
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

wtsapp_client = WhatsAppClient()
logger = logging.getLogger(__name__)
load_dotenv()
app = FastAPI()


# Request Models.
class WebhookRequestData(BaseModel):
    object: str = ""
    entry: List = []


@app.get("/webhook")
async def WhatsAppWebhook(request: Request):

    if request.query_params.get('hub.verify_token') == os.getenv("WHATSAPP_HOOK_TOKEN"):
        return int(request.query_params.get('hub.challenge'))
    else:
        raise HTTPException(status_code=400, detail="Failure")
    


def send_message(response, to):
    openai_client = OpenAIClient()
    reply = openai_client.complete(question=response["body"], sender_id=response["sender_id"] )
    if to=="whatsapp":
        wtsapp_client.send_text_message(message=reply, phone_number=response["sender_id"])
        
    else:
        r = httpx.post(
            "https://graph.facebook.com/v2.6/me/messages",
            params={"access_token": os.getenv("FACEBOOK_PAGE_TOKEN")},
            headers={"Content-Type": "application/json"},
            json={
                "recipient": {"id": response["sender_id"]},
                "message": {"text": reply},
                "messaging_type": "UPDATE",
            },
        )
        

@app.post("/webhook", status_code=status.HTTP_200_OK)
async def receiveMsg(request: Request, background_task: BackgroundTasks):
    
    data = await request.json()
    response = wtsapp_client.process_notification(data)

    if response["statusCode"] == 200:
        if response["body"] and response["from_no"]:
            background_task.add_task(send_message, response,"whatsapp")
            
    
    return jsonable_encoder({"status": "success"})




@app.get("/webhook/messenger")
async def MessengerWebhook(request: Request):
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
async def webhook(data: WebhookRequestData, background_task: BackgroundTasks):
    """
    Messages handler.
    """
    print("data", data)
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
                
                background_task.add_task(send_message, response,"facebook")


    return jsonable_encoder({"status": "success"})



import os
from fastapi import FastAPI, HTTPException, Request
import logging
from whatsapp_client import WhatsAppClient
from fastapi.encoders import jsonable_encoder
from openai_client import OpenAIClient
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()
app = FastAPI()

@app.get("/webhook")
async def root(request: Request):

    if request.query_params.get('hub.verify_token') == os.getenv("WHATSAPP_HOOK_TOKEN"):
        return int(request.query_params.get('hub.challenge'))
    else:
        raise HTTPException(status_code=400, detail="Failure")



@app.post("/webhook")
async def receiveMsg(request: Request):
    wtsapp_client = WhatsAppClient()
    data = await request.json()
    response = wtsapp_client.process_notification(data)
    print("am i called", response)

    if response["statusCode"] == 200:
        if response["body"] and response["from_no"]:
            openai_client = OpenAIClient()
            reply = openai_client.complete(question=response["body"])
            print ("\nreply is:"  + reply)
            wtsapp_client.send_text_message(message=reply, phone_number=response["from_no"], )
            print ("\nreply is sent to whatsapp cloud:" + str(response))
    
    return jsonable_encoder({"status": "success"})




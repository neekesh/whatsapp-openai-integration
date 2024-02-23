
import os
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks, status
import logging
from whatsapp_client import WhatsAppClient
from fastapi.encoders import jsonable_encoder
from openai_client import OpenAIClient
from dotenv import load_dotenv

wtsapp_client = WhatsAppClient()
logger = logging.getLogger(__name__)
load_dotenv()
app = FastAPI()


@app.get("/webhook")
async def root(request: Request):

    if request.query_params.get('hub.verify_token') == os.getenv("WHATSAPP_HOOK_TOKEN"):
        return int(request.query_params.get('hub.challenge'))
    else:
        raise HTTPException(status_code=400, detail="Failure")

def send_message(response):
    openai_client = OpenAIClient()
    
    reply = openai_client.complete(question=response["body"], phone_no=response["from_no"] )
    wtsapp_client.send_text_message(message=reply, phone_number=response["from_no"])


@app.post("/webhook", status_code=status.HTTP_200_OK)
async def receiveMsg(request: Request, background_task: BackgroundTasks):
    
    data = await request.json()
    response = wtsapp_client.process_notification(data)

    if response["statusCode"] == 200:
        if response["body"] and response["from_no"]:
            background_task.add_task(send_message, response)
            
    
    return jsonable_encoder({"status": "success"})




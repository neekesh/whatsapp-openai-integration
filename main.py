
from fastapi import FastAPI, Request
import logging
from whatsapp_client import WhatsAppClient
from fastapi.encoders import jsonable_encoder

logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/webhook")
async def root(request: Request):

    if request.query_params.get('hub.verify_token') == "1234":
        return int(request.query_params.get('hub.challenge'))




@app.post("/webhook")
async def receiveMsg(request: Request):
    wtsapp_client = WhatsAppClient()
    data = await request.json()
    response = wtsapp_client.process_notification(data)
    print("am i called", response)

    if response["statusCode"] == 200:
        if response["body"] and response["from_no"]:
            # openai_client = OpenAIClient()
            # reply = openai_client.complete(prompt=response["body"])
            # print ("\nreply is:"  + reply)
            wtsapp_client.send_text_message(message=response["body"], phone_number=response["from_no"], )
            print ("\nreply is sent to whatsapp cloud:" + str(response))
    
    return jsonable_encoder({"status": "success"})




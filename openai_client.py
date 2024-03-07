import openai
import time
import os
from dotenv import load_dotenv
from datastore import Datastore

load_dotenv()
datastore = Datastore()
class OpenAIClient:

    def complete(self, question, sender_id):
        client = openai.OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
 )

        assistant = client.beta.assistants.retrieve(
            os.environ.get("OPENAI_ASSISTANT_ID"),
            )
        thread_id = datastore.get(sender_id)
        if thread_id is None:
            thread = client.beta.threads.create()
            thread_id = thread.id
            datastore.create(chat_details={
                "sender_id": sender_id,
                "thread_id": thread.id
            })
        client.beta.threads.messages.create(
            thread_id=thread_id, role="user", content=question
        )

        run = client.beta.threads.runs.create(
            thread_id=thread_id, assistant_id=assistant.id
        )
        
        while True:
            run = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
                )
            if run.completed_at:
                time.sleep(5)
                messages = client.beta.threads.messages.list(thread_id=thread_id, order="desc")
                return messages.data[0].content[0].text.value

if __name__ == "__main__":
    client = OpenAIClient()
    load_dotenv()
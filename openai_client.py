import os
import openai
import time


from dotenv import load_dotenv
load_dotenv()

PROMPT = "Detailed description of how chat gpt builder will work just as detailed as you want "

class OpenAIClient:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        print ("\nopenai key is" + self.api_key + " and its type is " )

    def complete(self, question):
        client = openai.OpenAI(
            api_key=self.api_key
        )

        assistant = client.beta.assistants.retrieve(os.getenv("OPENAI_ASSISTANT_ID"))
        thread = client.beta.threads.create()
        client.beta.threads.messages.create(
            thread_id=thread.id, role="user", content=question
        )

        client.beta.threads.runs.create(
            thread_id=thread.id, assistant_id=assistant.id
        )

        # completed_run = wait_on_run(run, thread)

        time.sleep(30) # INSERTING DELAY HERE HELPED

        messages = client.beta.threads.messages.list(thread_id=thread.id, order="desc")
        new_message = messages.data[0].content[0].text.value
    
#         response = client.chat.completions.create(
# model="gpt-3.5-turbo",
#         #   prompt=PROMPT,
#         #   temperature=0.0,
#         #   max_tokens=256,
#         #   top_p=1,
#           messages = [
#               {"role": "user", "content": question}
#           ],
#         #   frequency_penalty=0,
#         #   presence_penalty=0,
#         )

        # print ("response form openai is :\n" + str(response.choices[0].message.content) + "\n")
        return new_message

if __name__ == "__main__":
    client = OpenAIClient()
    response = client.complete("how are you")
    print (response)
    
import os
import openai


from dotenv import load_dotenv
load_dotenv()

PROMPT = "Detailed description of how chat gpt builder will work just as detailed as you want "

class OpenAIClient:
    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        print ("\nopenai key is" + openai.api_key + " and its type is " + openai.api_type)

    def complete(self, question):
        response = openai.Completion.create(
          model="text-davinci-003",
          prompt=PROMPT,
          temperature=0.0,
          max_tokens=256,
          top_p=1,
          message = [
              {"role": "user", "content": question}
          ],
          frequency_penalty=0,
          presence_penalty=0,
        )

        print ("response form openai is :\n" + str(response) + "\n")
        return response.choices[0].text

if __name__ == "__main__":
    client = OpenAIClient()
    response = client.complete("how are you")
    print (response)
    
from dotenv import load_dotenv
import os
from openai import OpenAI


class ChatGPT:
  def __init__(self):
    load_dotenv()
    self.gptClient = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

  def getResponse(self):
    response = self.gptClient.chat.completions.create(
      model="gpt-3.5-turbo",
      messages=[
        {
          "role": "user", "content": "Hello, how are you?"
        }
      ],
    )

    print(response)

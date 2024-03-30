import os
from dotenv import load_dotenv
from openai import OpenAI
from pathlib import Path
import urllib.request


class ApiCall:
    def __init__(self):
        load_dotenv()
        self.gptClient = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.resourcePath = os.getenv("RESOURCE_PATH")
        self.audioPath = self.resourcePath + '/Audio'
        self.imagePath = self.resourcePath + '/Image'

    def callGpt(self):
        response = self.gptClient.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user", "content": "Hello, how are you?"
                }
            ],
        )

        print(response)

    def callDallE(self):
        response = self.gptClient.images.generate(
            model="dall-e-3",
            prompt="a cute cat with a hat on",
            size="1024x1024",
            quality="standard",
            n=1,
        )

        url = response.data[0].url
        
        # imageResult = urllib.request.urlretrieve(url, self.imagePath + "/result.jpg")

        imageResult = urllib.request.urlopen(url).read()

        with open(self.imagePath + "/result.jpg", mode="wb") as f:
            f.write(imageResult)
            f.close()

    def callTTS(self):
        speech_file_path = Path(__file__).parent.parent / "TTSFile/speech.mp3"
        response = self.gptClient.audio.speech.create(
            model="tts-1",
            voice="onyx",
            input="이것은 한글 테스트 입니다."
        )

        response.stream_to_file(speech_file_path)

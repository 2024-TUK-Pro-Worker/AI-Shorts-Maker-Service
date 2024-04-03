import json
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
        self.promptPath = self.resourcePath + '/Prompt'

    def callGpt(self):
        with open(f"{self.promptPath}/GPTPrompt.txt", "r") as GPTPrompt:
            requestCommand = GPTPrompt.read()
            GPTPrompt.close()


        response = self.gptClient.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system", "content": "너는 영상 시나리오를 제작하는 도구야",
                    "role": "user", "content": requestCommand
                }
            ],
        )

        messageData = json.loads(response.choices[0].message.content)

        print(messageData)

        return messageData

    def callDallE(self, prompt, filename):
        response = self.gptClient.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )

        url = response.data[0].url

        imageResult = urllib.request.urlopen(url).read()

        with open(f"{self.imagePath}/{filename}.jpg", mode="wb") as image:
            image.write(imageResult)
            image.close()

    def callTTS(self):
        speech_file_path = Path(__file__).parent.parent / "TTSFile/speech.mp3"
        response = self.gptClient.audio.speech.create(
            model="tts-1",
            voice="onyx",
            input="이것은 한글 테스트 입니다."
        )

        response.stream_to_file(speech_file_path)

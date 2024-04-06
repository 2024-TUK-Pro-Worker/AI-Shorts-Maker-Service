import os
from openai import OpenAI
import urllib.request


class ApiCall:
    def __init__(self):
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
                    "role": "system", "content": "너는 드라마 시나리오를 작성하는 작가야",
                    "role": "user", "content": requestCommand
                }
            ],
        )

        return response.choices[0].message.content

    def callDallE(self, prompt, filename):
        retryCnt = 0
        try:
            response = self.gptClient.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1792",
                quality="standard",
                n=1,
            )

            url = response.data[0].url

            imageResult = urllib.request.urlopen(url).read()

            with open(f"{self.imagePath}/{filename}.jpg", mode="wb") as image:
                image.write(imageResult)
                image.close()
        except:
            if retryCnt < 5:
                retryCnt += 1
                self.callDallE(prompt, filename)

    def getTTSVoiceList(self):
        return ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer']

    def callTTS(self, speech, voice, filename):
        speech_file_path = f"{self.audioPath}/{filename}.mp3"
        response = self.gptClient.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=speech
        )

        response.stream_to_file(speech_file_path)

import os
import pymysql
import urllib.request
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class ApiCall:
    def __init__(self):
        self.gptClient = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.resourcePath = f'{os.getenv("RESOURCE_PATH")}'
        self.imagePath = self.resourcePath + '/Image'
        self.promptPath = self.resourcePath + '/Prompt'

    def callGpt(self):
        print('__ GPT 프롬프트 생성 시작 __')

        promptType = ''

        print('__ GPT 프롬프트 내용 호출 시도 __')
        db = pymysql.connect(host=os.getenv('DB_HOST'), port=int(os.getenv('DB_PORT')), user=os.getenv('DB_USER'), password=os.getenv('DB_PW'),
                             db=os.getenv('DB_NAME'), charset=os.getenv('DB_CHARSET'))
        cur = db.cursor()
        cur.execute("SELECT content FROM prompt WHERE uuid = %s", (os.getenv('UUID'),))
        row = cur.fetchone()
        db.close()
        print('__ GPT 프롬프트 내용 호출 성공 __')

        if row is not None:
            promptType = 'Custom'

        print(f'__ 프롬프트 타입 {promptType} __')

        print('__ GPT 프롬프트 Base 파일 호출 및 정제 시도 __')
        with open(f"{self.promptPath}/{promptType}GPTPrompt.txt", "r") as GPTPrompt:
            requestCommand = GPTPrompt.read()
            GPTPrompt.close()

        if promptType == 'Custom':
            requestCommand = row[0] + "\n" + requestCommand
        print('__ GPT 프롬프트 Base 파일 호출 및 정제 성공 __')

        print('__ GPT API 요청 시도 __')
        response = self.gptClient.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system", "content": "너는 짧은 드라마 시나리오를 작성하는 작가야",
                    "role": "user", "content": requestCommand
                }
            ],
        )
        print('__ GPT API 요청 성공 __')

        print('__ GPT 프롬프트 생성 종료 __')
        return response.choices[0].message.content

    def callDallE(self, prompt, filename):
        retryCnt = 0
        try:
            print('__ Dall-E API 요청 시도 __')
            response = self.gptClient.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1792",
                quality="standard",
                n=1,
            )

            url = response.data[0].url
            print('__ Dall-E API 요청 성공 __')

            imageResult = urllib.request.urlopen(url).read()

            print('__ Dall-E 이미지 저장 시도 __')
            with open(f"{self.imagePath}/{filename}.jpg", mode="wb") as image:
                image.write(imageResult)
                image.close()
            print('__ Dall-E 이미지 저장 성공 __')
        except Exception as e:
            print(e)
            # if retryCnt < 1:
            #     retryCnt += 1
            #     print(f'__ Dall-E API 요청 재시도 __')
            #     self.callDallE(prompt, filename)

    def getTTSVoiceList(self):
        return ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer']

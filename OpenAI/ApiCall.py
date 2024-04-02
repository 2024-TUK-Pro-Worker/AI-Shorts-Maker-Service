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

    def callGpt(self):
        requestCommand = """
        흥미를 이끌 수 있는 영상 시나리오를 영상이 1분동안 이어질 수 있도록 작성해줘. 시나리오에는 주제와 등장인물 수, 등장인물에 대한 성별과 외부에 대해 작성되어 있어야해. 등장인물을 설명 할 때는 반드시 이름이 있어야하고, '등장인물 누구:'와 같이 등장인물 뒤에 이름을 표현해주어야 하고, 씬별로 구분 되어 있어야해. 씬은 최소 6개 이상 있어야해. 씬에는 장면에 어울리는 대사를 등장인물마다 1개 이상 작성해줘. 씬에 나오는 등장인물은 반드시 1개 이상의 대사가 작성되어야해. 그리고 주제는 앞에 '주제:'라고 표현해주고, 씬은 씬마다 번호를 지정하여 순서를 정해줘 그리고 순서는 '씬1'처럼 씬뒤에 번호를 붙여서 출력해줘. 씬에 인물들이 대화하는 장소를 설명, 장소에 대한 설명은 '장소:'라고 앞에 붙이고 작성해줘. 내가 말한 모든 지시사항에 대한 결과는 아래 작성된 json 형식에만 맞추어 작성해줘.
        '{
            "제목": "시나리오 제목",
            "주제": "주제에 대한 상세한 설명",
            "씬": [
                {
                    "장소": "장소에 대한 설명을 작성",
                    "상황" : "씬에 대한 상황을 설명하는 글 작성"
                    "등장인물": {
                        "등장인물 수": "등장인물 수를 작성"
                        "등장인물 이름": "등장인물 성별 정보"
                    },
                    "대사": {
                        "등장인물 이름": "등장인물의 씬에 맞는 대사"	          
                    }
                }
            ]
        }'
        """

        response = self.gptClient.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system", "content": "너는 영상 시나리오를 제작하는 도구야",
                    "role": "user", "content": requestCommand
                }
            ],
        )

        print('시나리오')
        print(response.choices[0].message.content, end='\n\n\n')

        print('시나리오 상세 내용 까기')
        messageData = json.loads(response.choices[0].message.content)
        for key in messageData.keys():
            print(key, end=' : ')
            print(messageData[key])
            if key == '씬':
                for scene in messageData[key]:
                    print(scene)

        return messageData

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

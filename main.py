import json
from OpenAI import callChatGPT, callDallE, callTTS

def makeResource (messageData):
    for key in messageData.keys():
        if key == '제목':
            messageData[key]
        elif key == '주제':
            messageData[key]
        elif key == '씬':
            sceneCount = 1
            for scene in messageData[key]:
                callDallE(f"{scene['장소']}에서 {scene['상황']} 그려줘", sceneCount)
                for name in scene['대사'].keys():
                    callTTS(scene['대사'][name], scene['등장인물'][name], f"{sceneCount}-{name}")
                sceneCount += 1
    return ''


if __name__ == '__main__':
    gptResponse = callChatGPT()
    makeResource(gptResponse)

    print(gptResponse)
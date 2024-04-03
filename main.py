import os
import json
import random
from OpenAI import callChatGPT, callDallE, callTTS, getTTSVoiceList

def makeResource (messageData):
    scenario = json.loads(messageData)
    characterVoice = {}

    for key in scenario.keys():
        if key == '제목':
            resourcePath = os.getenv("RESOURCE_PATH")
            title = scenario[key]
            os.mkdir(f"{resourcePath}/Audio/{title}")
            os.mkdir(f"{resourcePath}/Image/{title}")
            os.mkdir(f"{resourcePath}/Scenario/{title}")

            with open(f"{resourcePath}/Scenario/{title}/{title}.txt", "w") as scenarioFile:
                scenarioFile.write(messageData)
                scenarioFile.close()

        elif key == '씬':
            sceneIndex = 1
            for scene in scenario[key]:
                callDallE(f"{scene['장소']}에서 {scene['상황']} 그려줘", f"{title}/{sceneIndex}")

                for script in scene['대사']:
                    if characterVoice.get(script['이름']) is None:
                        characterVoice[script['이름']] = random.choice(getTTSVoiceList())
                    callTTS(script['스크립트'], characterVoice[script['이름']], f"{title}/{sceneIndex}-{script['순서']}")
                sceneIndex += 1
    return ''


if __name__ == '__main__':
    gptResponse = callChatGPT()
    makeResource(gptResponse)
import os
import json
import random
from pydub import *
from moviepy.editor import *
from dotenv import load_dotenv
from OpenAI import callChatGPT, callDallE, callTTS, getTTSVoiceList

load_dotenv()
resourcePath = os.getenv("RESOURCE_PATH")
title = ''


def makeResource(messageData):
    global title
    global resourcePath
    scenario = json.loads(messageData)
    characterVoice = {}

    for key in scenario.keys():
        if key == '제목':
            title = scenario[key]
            os.mkdir(f"{resourcePath}/Scenario/{title}")
            os.mkdir(f"{resourcePath}/Audio/{title}")
            os.mkdir(f"{resourcePath}/Image/{title}")
            os.mkdir(f"{resourcePath}/Video/{title}")

            with open(f"{resourcePath}/Scenario/{title}/{title}.txt", "w") as scenarioFile:
                scenarioFile.write(messageData)
                scenarioFile.close()

        elif key == '씬':
            sceneIndex = 1
            for scene in scenario[key]:
                imageFilename = f"{title}/{sceneIndex}"
                callDallE(f"{scene['장소']}에서 {scene['상황']} 그려줘", imageFilename)

                audioIndex = 1
                for script in scene['대사']:
                    if characterVoice.get(script['이름']) is None:
                        characterVoice[script['이름']] = random.choice(getTTSVoiceList())

                    callTTS(script['스크립트'], characterVoice[script['이름']], f"{title}/{sceneIndex}-{script['순서']}")

                    if audioIndex >= 2:
                        baseTTSFilename = f"{resourcePath}/Audio/{title}/{sceneIndex}-" + (
                            str((int(script['순서']) - 1)) if audioIndex == 2 else "TTS") + '.mp3'
                        baseTTS = AudioSegment.from_mp3(baseTTSFilename)
                        appendTarget = AudioSegment.from_mp3(
                            f"{resourcePath}/Audio/{title}/{sceneIndex}-{script['순서']}.mp3")
                        appendTTS = baseTTS + appendTarget
                        appendTTS.export(f"{resourcePath}/Audio/{title}/{sceneIndex}-TTS.mp3")

                    audioIndex += 1

                createVideo(sceneIndex)

                sceneIndex += 1


def createVideo(sceneIndex):
    global title
    global resourcePath
    # 동영상 생성할 때 duration을 오디오 파일과 동일하게 설정
    audio = AudioFileClip(f"{resourcePath}/Audio/{title}/{sceneIndex}-TTS.mp3")

    video = ImageClip(f"{resourcePath}/Image/{title}/{sceneIndex}.jpg", duration=audio.duration)
    video = video.set_audio(audio)
    video.write_videofile(f"{resourcePath}/Video/{title}/{sceneIndex}.mp4", fps=60, codec="mpeg4")


def makeShorts():
    global title
    global resourcePath

    video_list = sorted(os.listdir(f"{resourcePath}/Video/{title}"))
    video_clips = []
    for video in video_list:
        video_clip = VideoFileClip(f"{resourcePath}/Video/{title}/{video}")
        video_clips.append(video_clip)
    final_video_clip = concatenate_videoclips(video_clips)
    final_video_path = f"{resourcePath}/Upload/{title}.mp4"
    final_video_clip.write_videofile(final_video_path)


if __name__ == '__main__':
    gptResponse = callChatGPT()
    makeResource(gptResponse)
    makeShorts()

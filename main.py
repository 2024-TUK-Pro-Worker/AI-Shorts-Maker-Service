import os
import json
import random
import shutil
import pymysql
from pydub import *
from moviepy.editor import *
from dotenv import load_dotenv
from OpenAI import callChatGPT, callDallE
from Google import callTTS, getTTSVoiceList

load_dotenv()
resourcePath = os.getenv("RESOURCE_PATH")
uuid = os.getenv("UUID")
title = ''


def makeResource(messageData):
    global title
    global resourcePath
    scenario = json.loads(messageData)
    characterVoice = {}

    for key in scenario.keys():
        if key == '제목':
            title = scenario[key]

            if not os.path.isfile(f"{resourcePath}/Scenario/{title}.txt"):
                os.makedirs(f"{resourcePath}/Audio/{title}")
                os.makedirs(f"{resourcePath}/Image/{title}")
                os.makedirs(f"{resourcePath}/Video/{title}")

            with open(f"{resourcePath}/Scenario/{title}.txt", "w") as scenarioFile:
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

                    callTTS(script['스크립트'], characterVoice[script['이름']], f"{imageFilename}-{script['순서']}")

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
    global uuid
    global title
    global resourcePath

    videoList = sorted(os.listdir(f"{resourcePath}/Video/{title}"))
    videoClips = []
    for video in videoList:
        videoClip = VideoFileClip(f"{resourcePath}/Video/{title}/{video}")
        videoClips.append(videoClip)
    finalVideoClip = concatenate_videoclips(videoClips)
    finalVideoPath = f"{resourcePath}/Upload/tmp/{title}.mp4"
    finalVideoClip.write_videofile(finalVideoPath)

    db = pymysql.connect(host=os.getenv('DB_HOST'), port=int(os.getenv('DB_PORT')), user=os.getenv('DB_USER'),
                         password=os.getenv('DB_PW'),
                         db=os.getenv('DB_NAME'), charset=os.getenv('DB_CHARSET'))
    cur = db.cursor()
    sql = "INSERT INTO video (uuid, gptTitle) VALUES (%s, %s)"
    cur.execute(sql, (uuid, title))
    db.commit()
    db.close()

def removeResource():
    global title
    global resourcePath

    scenarioFile = f"{resourcePath}/Scenario/{title}.txt"
    audioDir = f"{resourcePath}/Audio/{title}"
    imageDir = f"{resourcePath}/Image/{title}"

    if os.path.isfile(scenarioFile):
        os.remove(scenarioFile)

    if os.path.isdir(audioDir):
        shutil.rmtree(audioDir)

    if os.path.isdir(imageDir):
        shutil.rmtree(imageDir)


if __name__ == '__main__':
    scenarioDir = f"{resourcePath}/Scenario"
    audioDir = f"{resourcePath}/Audio"
    imageDir = f"{resourcePath}/Image"
    videoDir = f"{resourcePath}/Video"
    uploadDir = f"{resourcePath}/Upload"
    uploadTmpDir = f"{resourcePath}/Upload/tmp"

    if not os.path.isdir(scenarioDir):
        os.makedirs(scenarioDir)
    if not os.path.isdir(audioDir):
        os.makedirs(audioDir)
    if not os.path.isdir(imageDir):
        os.makedirs(imageDir)
    if not os.path.isdir(uploadDir):
        os.makedirs(uploadDir)
    if not os.path.isdir(videoDir):
        os.makedirs(videoDir)
    if not os.path.isdir(uploadTmpDir):
        os.makedirs(uploadTmpDir)

    gptResponse = callChatGPT()
    makeResource(gptResponse)
    makeShorts()
    removeResource()

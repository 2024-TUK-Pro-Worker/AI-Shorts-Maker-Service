import os
import json
import random
import shutil
import pymysql
import datetime
from pydub import *
from moviepy.editor import *
from dotenv import load_dotenv
from OpenAI import callChatGPT, callDallE
from Google import callTTS, getTTSVoiceList

load_dotenv()
resourcePath = f'{os.getenv("RESOURCE_PATH")}'
uuid = os.getenv("UUID")
title = ''


def makeResource(messageData):
    print('__ 영상 리소스 제작 시작 __')

    global title
    global resourcePath
    scenario = json.loads(messageData)
    characterVoice = {}

    for key in scenario.keys():
        if key == '제목':
            print('__ 제목으로 리소스 path 생성 시도 __')

            title = scenario[key]

            if not os.path.isfile(f"{resourcePath}/Scenario/{title}.txt"):
                os.makedirs(f"{resourcePath}/Audio/{title}", mode=0o777)
                os.makedirs(f"{resourcePath}/Image/{title}", mode=0o777)
                os.makedirs(f"{resourcePath}/Video/{title}", mode=0o777)
            print('__ 제목으로 리소스 path 생성 성공 __')

            print('__ 시나리오 저장 시도 __')
            with open(f"{resourcePath}/Scenario/{title}.txt", "w") as scenarioFile:
                scenarioFile.write(messageData)
                scenarioFile.close()
            print('__ 시나리오 저장 성공 __')
        elif key == '씬':
            print('__ 씬별 리소스 제작 시작 __')
            sceneIndex = 1
            for scene in scenario[key]:
                print(f'__ {sceneIndex}번째 씬 리소스 제작 시작 __')
                imageFilename = f"{title}/{sceneIndex}"
                print(f'__ {sceneIndex}번째 씬 Dall-E API 요청 시도 __')
                callDallE(f"{scene['장소']}에서 {scene['상황']} 그려줘", imageFilename)
                print(f'__ {sceneIndex}번째 씬 Dall-E API 요청 성공 __')

                audioIndex = 1
                for script in scene['대사']:
                    if characterVoice.get(script['이름']) is None:
                        characterVoice[script['이름']] = random.choice(getTTSVoiceList())

                    print(f'__ {sceneIndex}번째 씬 대사 TTS 생성 시도 __')
                    callTTS(script['스크립트'], characterVoice[script['이름']], f"{imageFilename}-{script['순서']}")
                    print(f'__ {sceneIndex}번째 씬 대사 TTS 생성 성공 __')

                    print(f'__ {sceneIndex}번째 TTS 병합 작업 시도 __')
                    if audioIndex >= 2:
                        baseTTSFilename = f"{resourcePath}/Audio/{title}/{sceneIndex}-" + (
                            str((int(script['순서']) - 1)) if audioIndex == 2 else "TTS") + '.mp3'
                        baseTTS = AudioSegment.from_mp3(baseTTSFilename)
                        appendTarget = AudioSegment.from_mp3(
                            f"{resourcePath}/Audio/{title}/{sceneIndex}-{script['순서']}.mp3")
                        appendTTS = baseTTS + appendTarget
                        appendTTS.export(f"{resourcePath}/Audio/{title}/{sceneIndex}-TTS.mp3")

                    audioIndex += 1
                    print(f'__ {sceneIndex}번째 TTS 병합 작업 성공 __')

                print(f'__ {sceneIndex}번째 씬 영상 제작 __')
                createVideo(sceneIndex)
                print(f'__ {sceneIndex}번째 씬 영상 성공 __')

                print(f'__ {sceneIndex}번째 씬 리소스 제작 종료 __')

                sceneIndex += 1
            print('__ 씬별 리소스 제작 종료 __')
    print('__ 영상 리소스 제작 종료 __')


def createVideo(sceneIndex):
    global title
    global resourcePath
    # 동영상 생성할 때 duration을 오디오 파일과 동일하게 설정
    audio = AudioFileClip(f"{resourcePath}/Audio/{title}/{sceneIndex}-TTS.mp3")

    video = ImageClip(f"{resourcePath}/Image/{title}/{sceneIndex}.jpg", duration=audio.duration)
    video = video.set_audio(audio)
    video.write_videofile(f"{resourcePath}/Video/{title}/{sceneIndex}.mp4", fps=60, codec="mpeg4")


def makeShorts():
    print('__ 숏츠 제작 시작 __')

    global uuid
    global title
    global resourcePath

    print('__ 씬별 영상 병합 시도 __')
    videoList = sorted(os.listdir(f"{resourcePath}/Video/{title}"))
    videoClips = []
    for video in videoList:
        videoClip = VideoFileClip(f"{resourcePath}/Video/{title}/{video}")
        videoClips.append(videoClip)
    finalVideoClip = concatenate_videoclips(videoClips)
    finalVideoPath = f"{resourcePath}/Upload/tmp/{title}.mp4"
    finalVideoClip.write_videofile(finalVideoPath)
    print('__ 씬별 영상 병합 성공 __')

    print('__ 숏츠 영상 정보 저장 __')
    db = pymysql.connect(host=os.getenv('DB_HOST'), port=int(os.getenv('DB_PORT')), user=os.getenv('DB_USER'),
                         password=os.getenv('DB_PW'),
                         db=os.getenv('DB_NAME'), charset=os.getenv('DB_CHARSET'))
    cur = db.cursor()
    sql = "INSERT INTO video (uuid, gptTitle) VALUES (%s, %s)"
    cur.execute(sql, (uuid, title))
    db.commit()
    db.close()
    print('__ 숏츠 영상 정보 성공 __')

    print('__ 숏츠 제작 종료 __')

def removeResource():
    print('__ 영상 리소스 삭제 시작 __')

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

    print('__ 영상 리소스 삭제 종료 __')


if __name__ == '__main__':
    print(f'----------  시작 ({datetime.datetime.now()})  ----------')
    print('__ 디렉토리 검증 및 생성 시작 __')
    scenarioDir = f"{resourcePath}/Scenario"
    audioDir = f"{resourcePath}/Audio"
    imageDir = f"{resourcePath}/Image"
    videoDir = f"{resourcePath}/Video"
    uploadDir = f"{resourcePath}/Upload"
    uploadTmpDir = f"{resourcePath}/Upload/tmp"

    if not os.path.isdir(scenarioDir):
        os.makedirs(scenarioDir, mode=0o777)
    if not os.path.isdir(audioDir):
        os.makedirs(audioDir, mode=0o777)
    if not os.path.isdir(imageDir):
        os.makedirs(imageDir, mode=0o777)
    if not os.path.isdir(uploadDir):
        os.makedirs(uploadDir, mode=0o777)
    if not os.path.isdir(videoDir):
        os.makedirs(videoDir, mode=0o777)
    if not os.path.isdir(uploadTmpDir):
        os.makedirs(uploadTmpDir, mode=0o777)

    print('__ 디렉토리 검증 및 생성 종료 __')

    gptResponse = callChatGPT()
    makeResource(gptResponse)
    makeShorts()
    removeResource()
    print(f'----------  종료 ({datetime.datetime.now()})  ----------')

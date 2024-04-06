import os
import json
import random
import shutil
from pydub import *
from moviepy.editor import *
from dotenv import load_dotenv
from OpenAI import callChatGPT, callDallE, callTTS, getTTSVoiceList
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

load_dotenv()
resourcePath = os.getenv("RESOURCE_PATH")
title = ''

## OAuth 2.0 클라이언트 ID 및 스코프 설정
CLIENT_SECRET_FILE = './Config/client_secret.json'
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']


def makeResource(messageData):
    global title
    global resourcePath
    scenario = json.loads(messageData)
    characterVoice = {}

    for key in scenario.keys():
        if key == '제목':
            title = scenario[key]

            if not os.path.isfile(f"{resourcePath}/Scenario/{title}.txt"):
                os.mkdir(f"{resourcePath}/Audio/{title}")
                os.mkdir(f"{resourcePath}/Image/{title}")
                os.mkdir(f"{resourcePath}/Video/{title}")

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
    final_video_path = f"{resourcePath}/Upload/tmp/{title}.mp4"
    final_video_clip.write_videofile(final_video_path)


def appendBgm():
    global title
    global resourcePath

    bgmList = os.listdir(f"{resourcePath}/Bgm")
    bgm = random.choice(bgmList)

    # 비디오 파일과 새 오디오 파일 불러오기
    video = VideoFileClip(f"{resourcePath}/Upload/tmp/{title}.mp4")
    additional_audio = AudioFileClip(f"{resourcePath}/Bgm/{bgm}")

    # 기존 오디오와 새 오디오의 볼륨 조정(1.0이 기존 볼륨 크기 기준)
    original_audio = video.audio.volumex(2.0)
    additional_audio = additional_audio.volumex(0.3)

    # 조정된 볼륨으로 오디오 결합
    combined_audio = CompositeAudioClip([original_audio, additional_audio])

    # 비디오의 오디오를 결합된 오디오로 교체
    video = video.set_audio(combined_audio)

    # 결과 비디오 파일 저장(코덱: mp4 기준)
    video.write_videofile(f"{resourcePath}/Upload/{title}.mp4")


def get_authenticated_service():
    # OAuth 2.0 인증 흐름 초기화
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
    credentials = flow.run_local_server()

    # 인증된 서비스 반환
    return build('youtube', 'v3', credentials=credentials)


def upload_video(youtube, video_path, title, description, tags):
    try:
        # 동영상 업로드 정보 설정
        request_body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags
            },
            'status': {
                'privacyStatus': 'public'  # 동영상 공개 설정 (public, private, unlisted 중 선택)
            }
        }

        # 동영상 업로드 요청 생성
        media = MediaFileUpload(video_path)
        insert_request = youtube.videos().insert(
            part='snippet,status',
            body=request_body,
            media_body=media
        )

        # 동영상 업로드 실행
        response = insert_request.execute()

        # 업로드 성공 시 동영상 ID 반환
        if 'id' in response:
            print('동영상 업로드 완료. 동영상 ID:', response['id'])
        else:
            print('동영상 업로드 실패.')

    except HttpError as e:
        print('동영상 업로드 중 오류 발생:', e)


def youtubeUpload():
    global title
    global resourcePath

    # OAuth 2.0 인증 및 YouTube 서비스 생성
    youtube = get_authenticated_service()

    # 업로드할 동영상 파일 경로 설정
    video_path = f"{resourcePath}/Upload/{title}.mp4"

    # 업로드할 동영상 정보 설정
    description = title
    tags = ['생성형AI', 'AIShorts']

    upload_video(youtube, video_path, title, description, tags)


def removeResource():
    global title
    global resourcePath

    scenarioFile = f"{resourcePath}/Scenario/{title}.txt"
    audioDir = f"{resourcePath}/Audio/{title}"
    imageDir = f"{resourcePath}/Image/{title}"
    uploadTmpFile = f"{resourcePath}/Upload/tmp/{title}.mp4"

    if os.path.isfile(scenarioFile):
        os.remove(scenarioFile)

    if os.path.isdir(audioDir):
        shutil.rmtree(audioDir)

    if os.path.isdir(imageDir):
        shutil.rmtree(imageDir)

    if os.path.isfile(uploadTmpFile):
        os.remove(uploadTmpFile)


if __name__ == '__main__':
    # with open(f"{resourcePath}/Scenario/미스터리 쇼.txt", "r") as scenario:
    #     gptResponse = scenario.read()
    #     scenario.close()

    scenarioDir = f"{resourcePath}/Scenario"
    audioDir = f"{resourcePath}/Audio/{title}"
    imageDir = f"{resourcePath}/Image/{title}"
    uploadDir = f"{resourcePath}/Upload"
    uploadTmpDir = f"{resourcePath}/Upload/tmp"

    if not os.path.isdir(scenarioDir):
        os.mkdir(scenarioDir)
    if not os.path.isdir(audioDir):
        os.mkdir(audioDir)
    if not os.path.isdir(imageDir):
        os.mkdir(imageDir)
    if not os.path.isdir(uploadDir):
        os.mkdir(uploadDir)
    if not os.path.isdir(uploadTmpDir):
        os.mkdir(uploadTmpDir)

    gptResponse = callChatGPT()
    makeResource(gptResponse)
    makeShorts()
    appendBgm()
    # youtubeUpload()
    # removeResource()

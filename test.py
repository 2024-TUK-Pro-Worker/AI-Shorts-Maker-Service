import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

## OAuth 2.0 클라이언트 ID 및 스코프 설정
CLIENT_SECRET_FILE = './Config/client_secret_2.json'
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

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

if __name__ == '__main__':
    # OAuth 2.0 인증 및 YouTube 서비스 생성
    youtube = get_authenticated_service()

    # 업로드할 동영상 파일 경로 설정
    video_path = './Resource/test.mp4'  # 실제 동영상 파일 경로로 바꿔주세요.

    # 업로드할 동영상 정보 설정
    title = 'test'
    description = 'testtest'
    tags = ['test']  # 필요한 만큼 태그를 추가하세요.

    upload_video(youtube, video_path, title, description, tags)
# AI Shorts Maker Service

## 프로젝트 정보

### 설명
```text
본 프로젝트는 생성형 AI를 활용하여 숏츠를 자동으로 제작하여 유튜브에 업로드 하는 프로그램 입니다.
```

### 기술 스펙
```text
Language : Python (v3.11.8)
Tools : Kubernetes, Pycharm
Packages : requirements.txt 참조 
```

### 환경 설정 정보
```text
해당 프로젝트에서 사용중인 오디오 병합 작업에서는 pydud를 사용하고 있으며, OS에 ffmpeg를 설치해주셔야합니다.
macos : brew install ffmpeg 
```

### docker image 빌드 방법
```text
docker 이미지에 소스코드를 함께 빌드하는 방식으로 반드시 이미지를 구울 때 --build-arg token={developer_token} 을 옵션으로 넣어주어야 합니다.
```
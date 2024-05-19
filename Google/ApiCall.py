import os
from dotenv import load_dotenv
from google.cloud import texttospeech

load_dotenv()

class ApiCall:
    def __init__(self):
        self.resourcePath = f'{os.getenv("RESOURCE_PATH")}'
        self.audioPath = self.resourcePath + '/Audio'

    def getTTSVoiceList(self):
        return [
            'ko-KR-Neural2-A', 'ko-KR-Neural2-B', 'ko-KR-Neural2-C',
            'ko-KR-Wavenet-A', 'ko-KR-Wavenet-B', 'ko-KR-Wavenet-C', 'ko-KR-Wavenet-D'
        ]

    def callTTS(self, speech, voice, filename):
        print(f'__ Google TTS 호출 시도 __')

        client = texttospeech.TextToSpeechClient()

        # 최대 길이를 200으로 지정 (지나치게 길어지면 에러 발생)
        max_length = 200
        # . 단위로 문장 분리
        words = speech.split('. ')
        sentences = []
        current_sentence = ''
        for word in words:
            if len(current_sentence + word) <= max_length:
                current_sentence += word + ' '
            else:
                sentences.append(current_sentence.strip() + '.')
                current_sentence = word + ' '
        if current_sentence:
            sentences.append(current_sentence.strip() + '.')

        # 빈 배열 생성
        audio_data = []

        # 문장 개수 단위로 텍스트 변환
        for sentence in sentences:
            input_text = texttospeech.SynthesisInput(text=sentence)

            # 오디오 설정
            voice = texttospeech.VoiceSelectionParams(
                language_code="ko-KR",
                name=voice,
            )

            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                volume_gain_db=10.0
            )

            response = client.synthesize_speech(
                request={"input": input_text, "voice": voice, "audio_config": audio_config}
            )

            audio_data.append(response.audio_content)

        audio_data = b"".join(audio_data)
        print(f'__ Google TTS 호출 성공 __')

        # 파일 저장
        print(f'__ Google TTS 파일 저장 시도 __')
        with open(f"{self.audioPath}/{filename}.mp3", "wb") as out:
            out.write(audio_data)
        print(f'__ Google TTS 파일 저장 성공 __')

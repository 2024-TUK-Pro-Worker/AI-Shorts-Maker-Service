import os
from dotenv import load_dotenv
from openai import OpenAI
from pathlib import Path

class TTS:
  def __init__(self):
    load_dotenv()
    self.gptClient = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

  def getResponse(self):
    speech_file_path = Path(__file__).parent.parent / "TTSFile/speech.mp3"
    response = self.gptClient.audio.speech.create(
      model="tts-1",
      voice="onyx",
      input="이것은 한글 테스트 입니다."
    )

    response.stream_to_file(speech_file_path)

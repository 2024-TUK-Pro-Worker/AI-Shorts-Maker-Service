from .ApiCall import *


def callTTS(speech, voice, filename):
    return ApiCall().callTTS(speech, voice, filename)

def getTTSVoiceList():
    return ApiCall().getTTSVoiceList()
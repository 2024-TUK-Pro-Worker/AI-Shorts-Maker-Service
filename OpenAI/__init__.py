from .ApiCall import *


def callChatGPT():
    return ApiCall().callGpt()


def callDallE(prompt, filename):
    return ApiCall().callDallE(prompt, filename)


def callTTS(speech, voice, filename):
    return ApiCall().callTTS(speech, voice, filename)


def getTTSVoiceList():
    return ApiCall().getTTSVoiceList()

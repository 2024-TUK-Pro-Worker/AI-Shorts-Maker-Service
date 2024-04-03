from .ApiCall import *


def callChatGPT():
    return ApiCall().callGpt()


def callDallE(prompt, filename):
    return ApiCall().callDallE(prompt, filename)


def callTTS(speech, sex, filename):
    return ApiCall().callTTS(speech, sex, filename)

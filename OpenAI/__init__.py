from .ApiCall import *


def callChatGPT():
    return ApiCall().callGpt()


def callDallE():
    return ApiCall().callDallE()


def callTTS():
    return ApiCall().callTTS()

from OpenAI import callChatGPT, callTTS

chatgpt = callChatGPT()
tts = callTTS()

if __name__ == '__main__':
    # chatgpt.getResponse()
    tts.getResponse()
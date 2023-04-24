import speech_recognition as sr

# 创建语音识别对象
r = sr.Recognizer()

# 使用麦克风录制语音
with sr.Microphone() as source:
    print("请说话...")
    audio = r.listen(source)
# print("录音完毕！")

# 将语音转换为文本
try:
    text = r.recognize_google(audio, language='zh-CN')
    print("User: " + text)
except sr.UnknownValueError:
    print("抱歉，无法识别你的语音")
except sr.RequestError as e:
    print("请求出错：" + str(e))

import openai
from aip import AipSpeech
from playsound import playsound
import speech_recognition as sr


def t2a():
    while True:
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
            print("User: " + text + "\n")
            return text
        except sr.UnknownValueError:
            f = input("抱歉，无法识别你的语音，重新识别？输入“Y”确认，输入其它字符重新选择输入模式。")
            if f == 'Y' or f == 'y':
                continue
            else:
                return -1
        except sr.RequestError as e:
            print("请求出错：" + str(e))
            return -1


def a2t(text):
    """ 你的 APPID AK SK """
    APP_ID = '31556395'
    API_KEY = 'G7sUbyYs1Lyd7M6yamv1jlEj'
    SECRET_KEY = 'edjBrsfpQmTGuOxoPG6o4HIqqIj1RjTM'

    client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)
    result = client.synthesis(text, 'zh', 1, {
        'vol': 5,
        'per': 1
    })

    # 识别正确返回语音二进制 错误则返回dict 参照下面错误码
    if not isinstance(result, dict):
        with open('temp.mp3', 'wb') as f:
            f.write(result)
    playsound('temp.mp3')


openai.api_key = "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"
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "接下来的回答不要超过30字。"},
    {"role": "assistant", "content": "好的，我会尽力遵守您的要求。有什么可以帮您的吗？"},
    {"role": "user", "content": "你好。"}
]

try:
    while True:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        ans = completion.choices[0].message
        messages.append(ans)
        print(ans.role + ": " + ans.content + '\n')

        a2t(ans.content)

        while True:
            flag = input("选择输入模式，”t“为文本，”v”为语音：")
            if flag == 't':
                messages.append({"role": "user", "content": input("User: ")})
                print()
                break
            elif flag == 'v':
                t = t2a()
                if t == -1:
                    continue
                messages.append({"role": "user", "content": t})
                break
            else:
                print("重新输入模式！")
                continue
except KeyboardInterrupt:
    pass
print('Range over!')

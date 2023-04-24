import openai
from aip import AipSpeech
from playsound import playsound
import speech_recognition as sr
import pyttsx3
import wake


def google_a2t():
    # 创建语音识别对象
    r = sr.Recognizer()

    while True:
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
            pyttsx_t2a("你搁这说啥呢？")
            continue
        except sr.RequestError as e:
            print("请求出错：" + str(e))
            return -1


def baidu_t2a(text):
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


def pyttsx_t2a(text):
    x = pyttsx3.init()
    x.say(text)
    x.runAndWait()


if __name__ == "__main__":
    openai.api_key = "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"
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "接下来的回答不要超过30字。"},
        {"role": "assistant", "content": "好的，我会尽力遵守您的要求。有什么可以帮您的吗？"},
    ]

    try:
        while True:
            wake.wake()
            while True:
                flag = 0
                # 语音输入
                while True:
                    t = google_a2t()
                    if t == -1:
                        # raise error
                        continue
                    elif t in ["再见", "退下吧", "拜拜"]:
                        pyttsx_t2a("爷走咯！")
                        flag = 1
                        break
                    messages.append({"role": "user", "content": t})
                    break
                if flag == 1:
                    break

                completion = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=messages
                )

                ans = completion.choices[0].message
                messages.append(ans)
                print(ans.role + ": " + ans.content + '\n')
                pyttsx_t2a(ans.content)

    except KeyboardInterrupt:
        pass
    print('Range over!')

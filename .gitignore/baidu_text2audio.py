from aip import AipSpeech

""" 你的 APPID AK SK """
APP_ID = '31556395'
API_KEY = 'G7sUbyYs1Lyd7M6yamv1jlEj'
SECRET_KEY = 'edjBrsfpQmTGuOxoPG6o4HIqqIj1RjTM'

client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)
result = client.synthesis('how are you', 'zh', 1, {
    'vol': 5,
})
# print(result)

# 识别正确返回语音二进制 错误则返回dict 参照下面错误码
if not isinstance(result, dict):
    with open('aud.mp3', 'wb') as f:
        f.write(result)

from playsound import playsound

playsound('aud.mp3')




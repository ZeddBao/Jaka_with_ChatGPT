#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
import sys
import base64
import time

IS_PY3 = sys.version_info.major == 3

if IS_PY3:
    from urllib.request import urlopen
    from urllib.request import Request
    from urllib.error import URLError
    from urllib.parse import urlencode

    timer = time.perf_counter
else:
    from urllib2 import urlopen
    from urllib2 import Request
    from urllib2 import URLError
    from urllib import urlencode

    if sys.platform == "win32":
        timer = time.clock
    else:
        # On most other platforms the best timer is time.time()
        timer = time.time

import ssl

ssl._create_default_https_context = ssl._create_unverified_context

# 填写百度控制台中相关开通了“语音合成”接口的应用的的API_KEY及SECRET_KEY
API_KEY = '****'
SECRET_KEY = '****'

"""  获取请求TOKEN start 通过开通语音合成接口的百度应用的API_KEY及SECRET_KEY获取请求token"""


class DemoError(Exception):
    pass


TOKEN_URL = 'https://openapi.baidu.com/oauth/2.0/token'
SCOPE = 'audio_tts_post'  # 有此scope表示有tts能力，没有请在网页里勾选


def fetch_token():
    params = {'grant_type': 'client_credentials',
              'client_id': 'G7sUbyYs1Lyd7M6yamv1jlEj',
              'client_secret': 'edjBrsfpQmTGuOxoPG6o4HIqqIj1RjTM'}
    post_data = urlencode(params)
    if (IS_PY3):
        post_data = post_data.encode('utf-8')
    req = Request(TOKEN_URL, post_data)
    try:
        f = urlopen(req)
        result_str = f.read()
    except URLError as err:
        print('token http response http code : ' + str(err.code))
        result_str = err.read()
    if (IS_PY3):
        result_str = result_str.decode()

    #    print(result_str)
    result = json.loads(result_str)
    #    print(result)
    if ('access_token' in result.keys() and 'scope' in result.keys()):
        if not SCOPE in result['scope'].split(' '):
            raise DemoError('scope is not correct')
        #        print('SUCCESS WITH TOKEN: %s ; EXPIRES IN SECONDS: %s' % (result['access_token'], result['expires_in']))
        return result['access_token']
    else:
        raise DemoError('MAYBE API_KEY or SECRET_KEY not correct: access_token or scope not found in token response')


"""  获取鉴权结束，TOKEN end """

"""  发送查询结果请求 """

# 长文本合成任务id列表，支持同时查询多个，task_id是通过创建长文本合成任务时获取到的每个合成任务对应的值
task_id_list = [
    "641b470aea05a00001898cd8"
]

url = 'https://aip.baidubce.com/rpc/2.0/tts/v1/query'  # 查询长文本语音合成任务结果请求地址

body = {
    "task_ids": task_id_list
}

token = {"access_token": fetch_token()}

headers = {'content-type': "application/json"}

response = requests.post(url, params=token, data=json.dumps(body), headers=headers)

print(json.dumps(response.json(), ensure_ascii=False))

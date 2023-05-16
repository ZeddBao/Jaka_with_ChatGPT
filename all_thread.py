import os
import time
import datetime
import openai
import cv2
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
import all_gpt
from AIDetector_pytorch import Detector
import numpy as np
import speech_recognition as sr
import requests
import pyttsx3
from pocketsphinx import LiveSpeech
import re
import random
import json
from deepface import DeepFace
import pyrealsense2 as rs
import jkrc
import emotions
from main import robot
from PIL import Image
import io

with open('config.json') as f:
    config = json.load(f)
max_lose_count = config["max_lose_count"]
max_attention_count = config["max_attention_count"]
random_count = config["random_count"]

PI = 3.1415926
ABS = 0  # 绝对运动
INCR = 1  # 增量运动
Enable = True
Disable = False


class PhotoVariationThread(QThread):
    photo = None
    date = None
    time = None
    n = 1

    def __int__(self):
        super().__init__()

    def set_photo(self, photo, date, current_time, n=1):
        self.photo = photo
        self.date = date
        self.time = current_time
        self.n = n

    def run(self):
        # 读取原始图像
        image = self.photo

        # 获取原始图像的宽度和高度
        height, width = image.shape[:2]

        # 计算裁剪区域的左上角和右下角坐标
        left = (width - 480) // 2
        top = (height - 480) // 2
        right = left + 480
        bottom = top + 480

        # 裁剪图像
        cropped_image = image[top:bottom, left:right]
        cropped_image = np.ascontiguousarray(cropped_image)

        # 将OpenCV图像转换为PIL Image格式，并保存为PNG格式
        cropped_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB)
        with io.BytesIO() as output:
            Image.fromarray(cropped_image).save(output, format='PNG')
            png_image = output.getvalue()

        # 将PNG图像传递给OpenAI API进行转换
        openai.api_key = os.getenv("OPENAI_API_KEY")
        response = openai.Image.create_variation(
            image=png_image,
            n=self.n,
            size="256x256"
        )
        urls = [data['url'] for data in response['data']]
        print(urls)
        for url in urls:
            t = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            response = requests.get(url)
            with open("photo\\" + self.date + "\\" + self.time + "_variation.jpg", "wb") as f:
                f.write(response.content)


class VideoThread(QThread):
    # 硬件相关
    robot = None
    det = Detector()
    video_writer = None
    depth_camera_flag = True
    record_timer = QTimer()
    track_timer = QTimer()

    # 信号相关
    frame_ready = pyqtSignal(np.ndarray)
    lose_signal = pyqtSignal()
    # obj_ready = pyqtSignal(list)
    text_signal = pyqtSignal(str)
    button_signal = pyqtSignal(str)
    target_info_signal = pyqtSignal(list)
    ref_info_signal = pyqtSignal(list)
    resolution_info_signal = pyqtSignal(list)
    robot_position_info_signal = pyqtSignal(list)

    # 追踪器相关
    mode = "normal"
    frame = None
    obj_info = []
    depth_image = None
    enable = enable_track = enable_record = False
    target_id = 0
    target_info = None
    attention_id = 0
    w = h = 0
    rx = ry = 0
    x_output = y_output = 0
    size = 0
    count = lose_count = attention_count = 0

    # 拍摄相关
    cap_interval = 33
    hd = vd = 0
    sf = 1

    # 照片修改线程
    photo_variation = PhotoVariationThread()

    def __init__(self, camera_index=0):
        super().__init__()
        self.camera_index = camera_index
        self.cap = cv2.VideoCapture(self.camera_index)
        self.record_timer.timeout.connect(self.record)
        self.track_timer.timeout.connect(lambda: self.track(self.x_output, self.y_output))
        try:
            self.pipeline = rs.pipeline()
            config = rs.config()
            config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
            self.pipeline.start(config)  # 开始采集深度图像
        except RuntimeError:
            self.text_signal.emit("System: 深度相机初始化失败！")
            self.depth_camera_flag = False

    def run(self):
        s = time.time()
        self.enable = True
        self.count = 0

        while self.enable:
            # start_time = time.time()
            # 读取视频帧
            ret, frame = self.cap.read()
            self.frame = frame.copy()
            if not ret:  # 读取失败
                break
            if self.depth_camera_flag:  # 如果深度相机可用
                frames = self.pipeline.wait_for_frames()  # 等待一帧
                self.depth_image = np.asanyarray(frames.get_depth_frame().get_data())  # 将深度图像转换为OpenCV格式

            # 保存视频
            # if self.enable_record:
            #     self.record()

            if self.rx == 0:  # 初始化参考点
                self.w = frame.shape[1]
                self.h = frame.shape[0]
                self.size = self.w * self.h
                self.rx = frame.shape[1] / 2
                self.ry = 2 * frame.shape[0] / 3
                self.resolution_info_signal.emit([self.w, self.h])
                self.ref_info_signal.emit([self.rx, self.ry])

            # 进行目标检测
            result = self.det.feedCap(frame)  # 传入视频帧
            self.obj_info = result['obj_info']  # 获取目标信息
            self.frame_ready.emit(result['frame'])  # 发送视频帧

            if self.mode == "lose_random" and self.lose_count > max_lose_count and self.obj_info:  # 丢失目标
                self.target_id = random.choice(self.obj_info)[0]
                self.text_signal.emit("System: 已设置目标ID为" + str(self.target_id) + "！\n")
                self.lose_count = 0  # 重置丢失计数器
            elif self.mode == "random" and self.count % random_count == 0 and self.obj_info:  # 随机切换目标
                self.target_id = random.choice(self.obj_info)[0]
                self.text_signal.emit("System: 已设置目标ID为" + str(self.target_id) + "！\n")
            elif self.mode == "attention" and self.attention_count > max_attention_count:
                self.target_id = self.attention_id
                self.text_signal.emit("System: 已设置目标ID为" + str(self.target_id) + "！\n")
                self.attention_count = 0  # 重置关注计数器
            elif self.mode == "lose_attention" and self.lose_count > max_lose_count and self.attention_count > max_attention_count:
                self.target_id = self.attention_id
                self.text_signal.emit("System: 已设置目标ID为" + str(self.target_id) + "！\n")
                self.attention_count = 0  # 重置关注计数器
                self.lose_count = 0  # 重置丢失计数器

            self.calculate_data(self.target_id, self.rx, self.ry, self.mode)  # 计算输出
            self.count += 1  # 计数器+1
            # time.sleep(0.04)
            # end_time = time.time()
            # print(end_time-start_time)

        self.rx = self.ry = 0  # 重置参考点
        self.w = self.h = 0  # 重置分辨率
        self.size = 0  # 重置画面大小
        self.x_output = self.y_output = 0  # 重置输出
        e = time.time()
        print("avr", (e - s) / self.count)
        self.count = self.lose_count = self.attention_count = 0  # 重置计数器

    def calculate_data(self, tid, rx, ry, mode):
        flag = 0  # 是否找到目标标记

        for obj in self.obj_info:  # 遍历所有目标
            if obj[0] == tid:  # 找到目标
                flag = 1  # 标记找到目标
                self.target_info = obj  # 更新目标信息
                self.lose_count = 0  # 重置丢失计数器
                ex = round(obj[1] - rx, 2)  # 计算目标与参考点的x轴距离
                ey = round(obj[2] - ry, 2)  # 计算目标与参考点的y轴距离
                if ex > 30:
                    x_output = -0.005
                elif ex < -30:
                    x_output = 0.005
                else:
                    x_output = 0
                if ey > 50:
                    y_output = 0.0003
                elif ey < -50:
                    y_output = -0.0003
                else:
                    y_output = 0
                self.x_output = x_output
                self.y_output = y_output

                if self.robot is not None:  # 是否开启追踪并且机械臂是否已连接
                    if self.count % 10 == 0:  # 每10次发送一次机械臂位置信息
                        robot_joint = robot.get_joint_position()  # 获取机械臂关节角度
                        if robot_joint[0] == 0:  # 机械臂已连接，获取成功
                            robot_joint = [round(num, 2) for num in robot_joint[1]]
                        else:  # 机械臂未连接，获取失败
                            robot_joint = [-1, -1, -1, -1, -1, -1]
                        robot_tcp = self.robot.get_tcp_position()  # 获取机械臂末端位置
                        if robot_tcp[0] == 0:  # 机械臂已连接，获取成功
                            robot_tcp = [round(num, 2) for num in robot_tcp[1]]
                        else:  # 机械臂未连接，获取失败
                            robot_tcp = [-1, -1, -1, -1, -1, -1]
                        self.robot_position_info_signal.emit([robot_joint, robot_tcp])
                if self.count % 10 == 0:  # 每10帧发送一次目标位置信息
                    self.target_info_signal.emit([obj[1], obj[2], obj[3], ex, ey, x_output, y_output])
                break

        if flag == 0:  # 未找到目标
            self.target_info = None  # 重置目标信息
            self.x_output = self.y_output = 0  # 重置输出
            # if mode == "lose_random" or mode == "lose_attention":
            self.lose_count += 1
            if self.count % 10 == 0:  # 每10帧发送一次信号
                self.target_info_signal.emit([0, 0, 0, 0, 0, 0, 0])

        if mode == "attention" and self.obj_info or mode == "lose_attention" and self.obj_info:
            max_obj = max(self.obj_info, key=lambda x: x[3])  # 找到最大目标
            if max_obj[3] > self.size / 4:  # 最大目标大于1/4画面面积
                if max_obj[0] == self.attention_id:  # 最大目标为关注目标
                    self.attention_count += 1  # 关注计数器+1
                else:
                    self.attention_count = 0  # 重置关注计数器
                self.attention_id = max_obj[0]

    def track(self, x_output, y_output):
        if self.robot is not None and self.robot.is_in_pos()[1] == 1 and self.robot.is_in_collision()[1] == 0:
            # 是否开启追踪并且机械臂是否已连接
            robot.servo_move_enable(True)
            robot.servo_j(
                joint_pos=[x_output / 5, -y_output, 2 * y_output, -y_output, x_output, 0], move_mode=1)

    def stop(self):
        self.enable = False
        self.record_timer.stop()

    def toggle_track(self):
        self.enable_track = not self.enable_track

    def toggle_record(self):
        self.enable_record = not self.enable_record

    def modify(self, frame, hue_delta=0, saturation_factor=1.0, value_delta=0):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        h = np.clip(h + hue_delta, 0, 179).astype(np.uint8)
        s = np.clip(s * saturation_factor, 0, 255).astype(np.uint8)
        v = np.clip(v + value_delta, 0, 255).astype(np.uint8)
        hsv = cv2.merge((h, s, v))
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    def record(self):
        frame = self.frame.copy()
        if self.hd != 0 or self.sf != 1 or self.vd != 0:
            frame = self.modify(frame, self.hd, self.sf, self.vd)
        self.video_writer.write(frame)

    def set_camera(self, index):
        self.stop()
        self.wait()
        self.button_signal.emit("打开摄像头")
        self.cap.release()
        self.camera_index = index
        self.cap = cv2.VideoCapture(index)

    def update_ref(self, x, y, w, h):
        self.rx = round(x / w * self.w, 2)
        self.ry = round(y / h * self.h, 2)
        self.ref_info_signal.emit([self.rx, self.ry])

    def change_ref(self, x, y):
        self.rx = x
        self.ry = y
        self.ref_info_signal.emit([self.rx, self.ry])

    def change_mode(self, mode):
        self.mode = mode

    def save_photo(self, comments):
        date = str(datetime.datetime.now().strftime('%Y-%m-%d'))
        current_time = str(datetime.datetime.now().strftime('%H_%M_%S'))
        if not os.path.exists("photo/" + date):
            os.mkdir("photo/" + date)
        if self.frame is not None:
            cv2.imwrite("photo/" + date + "/" + current_time + ".png", self.frame, [cv2.IMWRITE_PNG_COMPRESSION, 6])
        with open("photo/" + date + "/" + current_time + ".txt", "w") as f:
            f.write(comments)
        self.photo_variation.set_photo(self.frame, date, current_time)
        self.text_signal.emit("System：照片保存成功！\n")
        self.photo_variation.start()
        self.text_signal.emit("CameraBot：正在施加魔法~\n")


class Audio2TextThread(QThread):
    text_signal = pyqtSignal(str)
    ans_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def run(self):  # 考虑使用多进程
        # 创建语音识别对象
        r = sr.Recognizer()
        # 使用麦克风录制语音
        with sr.Microphone() as source:
            self.text_signal.emit("请说话...")
            audio = r.listen(source)
        # 将语音转换为文本
        try:
            text = r.recognize_google(audio, language='zh-CN')
            self.ans_signal.emit(text)
        except sr.UnknownValueError:
            self.text_signal.emit("无法识别")
        except sr.RequestError as e:
            self.text_signal.emit("请求出错：" + str(e))


class Audio2TextThreadAuto(Audio2TextThread):
    enable_a2t = False

    def __int__(self):
        super().__init__()

    def run(self):
        while self.enable_a2t:
            # 创建语音识别对象
            r = sr.Recognizer()
            # 使用麦克风录制语音
            with sr.Microphone() as source:
                self.text_signal.emit("System：请说话...")
                audio = r.listen(source)
            # 将语音转换为文本
            try:
                text = r.recognize_google(audio, language='zh-CN')
                self.text_signal.emit("User：" + text)
            except sr.UnknownValueError:
                self.text_signal.emit("System：无法识别")
            except sr.RequestError as e:
                self.text_signal.emit("System：请求出错：" + str(e))

    def stop(self):
        self.enable_a2t = False


class GetAnsThread(QThread):
    enable_say = False
    ans_signal = pyqtSignal(str)
    gpt_signal = pyqtSignal(all_gpt.GPT)
    cmd_signal = pyqtSignal(list)

    def __init__(self, question="你好", gpt=all_gpt.GPT()):
        super().__init__()
        self.question = question
        self.gpt = gpt

    def run(self):

        ans = self.gpt.get_answer_context(self.question)
        if ans == -1:
            self.ans_signal.emit("System：连接错误！\n")
            return
        if ans == -2:
            self.ans_signal.emit("System：参数无效或账户权限问题！\n")
            return

        code, instructions, ans = text_process(ans)  # 语义分析
        if instructions:
            self.cmd_signal.emit(instructions)
        if code == "":
            self.ans_signal.emit("System：" + ans + "\n")
            if self.enable_say:
                text2audio(ans)
        else:
            write_code(code)
            flag = os.system("python temp.py")
            if flag != 0:
                self.ans_signal.emit("System：动作执行失败！\n")
                if self.enable_say:
                    text2audio("动作执行失败！")
            else:
                self.ans_signal.emit("System：动作执行完毕！\n")
                if self.enable_say:
                    text2audio("动作执行完毕！")

        self.gpt_signal.emit(self.gpt)  # 更新gpt模型

    def toggle_say(self):
        self.enable_say = not self.enable_say
        self.ans_signal.emit("System：语音播报已" + ("开启" if self.enable_say else "关闭") + "！\n")


class RecordThread(QThread):
    enable_record = False

    def __int__(self, camera_index=0):
        super().__init__()
        self.camera_index = camera_index
        self.cap = cv2.VideoCapture(self.camera_index)

    def run(self):
        video_writer = None
        while self.enable_record:
            ret, im = self.cap.read()
            if not ret:  # 读取失败
                break
            if video_writer is None:
                fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
                video_writer = cv2.VideoWriter('result.mp4', fourcc, 30, (im.shape[1], im.shape[0]))
            video_writer.write(im)
            time.sleep(0.33)

    def stop(self):
        self.enable_record = False


class WakeThreadNormal(QThread):
    question = None
    enable_wake = False

    ans_signal = pyqtSignal(str)
    gpt_signal = pyqtSignal(all_gpt.GPT)
    cmd_signal = pyqtSignal(list)

    def __init__(self, gpt=all_gpt.GPT()):
        super().__init__()
        self.gpt = gpt

    def run(self):
        self.enable_wake = True
        while self.enable_wake:
            wake()
            while self.enable_wake:
                flag = 0
                # 语音输入
                while self.enable_wake:
                    self.question = self.audio2text()
                    if self.question == -1:
                        continue
                    elif self.question in ["再见", "退下吧", "拜拜", "再見", "拜拜拜拜"]:
                        text2audio("爷走咯！")
                        flag = 1
                        break  # 退出一级循环

                    ans = self.gpt.get_answer_context(self.question)
                    if ans == -1:
                        self.ans_signal.emit("System：连接错误！\n")
                        flag = 1
                        break
                    if ans == -2:
                        self.ans_signal.emit("System：参数无效或账户权限问题！\n")
                        flag = 1
                        break

                    code, instructions, ans = text_process(ans)
                    if instructions:
                        self.cmd_signal.emit(instructions)
                    if code == "":
                        self.ans_signal.emit("System：" + ans + "\n")
                        text2audio(ans)
                    else:
                        write_code(code)
                        flag = os.system("python temp.py")
                        if flag != 0:
                            self.ans_signal.emit("System：动作执行失败！\n")
                            text2audio("动作执行失败！")
                        else:
                            self.ans_signal.emit("System：动作执行完毕！\n")
                            text2audio("动作执行完毕！")

                    self.gpt_signal.emit(self.gpt)  # 更新gpt模型

                if flag:
                    break  # 退出二级循环

    def stop(self):
        self.enable_wake = False

    def audio2text(self):
        # 创建语音识别对象
        r = sr.Recognizer()
        # 使用麦克风录制语音
        with sr.Microphone() as source:
            self.ans_signal.emit("System: 请说话...\n")
            audio = r.listen(source)
        # 将语音转换为文本
        try:
            text = r.recognize_google(audio, language='zh-CN')
            self.ans_signal.emit("User: " + text + "\n")
            return text
        except sr.UnknownValueError:
            self.ans_signal.emit("System: 无法识别语音!请重试！\n")
            text2audio("无法识别语音!请重试！")
            return -1
        except sr.RequestError as e:
            self.ans_signal.emit("System: 请求出错：" + str(e) + "\n")
            text2audio("请求出错!请重试！")
            return -1


class WakeThreadAuto(WakeThreadNormal):
    def __init__(self):
        super().__init__()

    def run(self):
        self.enable_wake = True
        while self.enable_wake:
            wake()
            while self.enable_wake:
                flag = 0
                # 语音输入
                while self.enable_wake:
                    prompt = self.audio2text()
                    if prompt == -1:
                        continue
                    elif prompt in ["再见", "退下吧", "拜拜", "再見", "拜拜拜拜"]:
                        flag = 1
                        break  # 退出一级循环

                    self.ans_signal.emit(prompt)
                if flag:
                    break  # 退出二级循环


class AnalyzeFaceThread(QThread):
    result_signal = pyqtSignal(dict)

    def __init__(self, face):
        super().__init__()
        self.face = face

    def run(self):
        result = DeepFace.analyze(self.face, actions=('gender', 'age', 'emotion'), enforce_detection=False)
        self.result_signal.emit(result[0])


def text2audio(text):
    pyttsx3.speak(text)


def get_code(text):
    pattern = re.compile(r"```python(.*?)```", re.S)
    match = pattern.findall(text)
    if match:
        return match[0], pattern.sub("", text)
    pattern = re.compile(r"```(.*?)```", re.S)
    match = pattern.findall(text)
    if match:
        return match[0], pattern.sub("", text)
    return "", text


def write_code(code):
    with open("example.txt", "r") as f:
        example = f.read()
    code = example.replace("# replace the text", code)
    with open("temp.py", "w") as f:
        f.write(code)


def text_process(text):  # 返回代码，指令，剩下的文本
    digit = []
    cmd = []
    code, text = get_code(text)
    pattern = re.compile(r"@@(.*?)@@")
    match = pattern.findall(text)
    text = pattern.sub("", text)
    pattern = re.compile(r"\d+")
    # 找到字符串中的数字，返回该数字和剩下的文本
    for match_text in match:
        digits = pattern.findall(match_text)
        if digits:
            digit.append(int(digits[0]))
            cmd.append(match_text.replace(digits[0], ""))
        else:
            digit.append(None)
            cmd.append(match_text)
    instructions = list(zip(cmd, digit))
    return code, instructions, text


def wake():
    model_path = r"D:\Users\baoze\anaconda3\envs\MechanicalArms\Lib\site-packages\pocketsphinx\model\cmusphinx-zh-cn-5.2"
    x = pyttsx3.init()

    speech = LiveSpeech(
        verbose=False,
        sampling_rate=16000,
        buffer_size=2048,
        no_search=False,
        full_utt=False,
        hmm=os.path.join(model_path, 'zh_cn.cd_cont_5000'),
        lm=os.path.join(model_path, '4789.lm'),
        dic=os.path.join(model_path, '4789.dic')
    )
    for phrase in speech:
        print("phrase:", phrase)
        print(phrase.segments(detailed=True))
        # 只要命中上述关键词的内容，都算对
        if str(phrase) in ["形影", "形影 形影", "形影 形影 形影", "啊 形影", "哈哈 形影"]:
            x.say("爷来咯！")
            x.runAndWait()
            return


class EmotionThread(QThread):
    emotion = None

    def __int__(self):
        super().__init__()

    def run(self):
        if self.emotion == "happy":
            emotions.happy()
        elif self.emotion == "sad":
            emotions.sad()
        elif self.emotion == "angry":
            emotions.angry()
        elif self.emotion == "surprise":
            # os.system("python emotion/surprise.py")
            pass
        elif self.emotion == "fear":
            emotions.fear()
        elif self.emotion == "disgust":
            # os.system("python emotion/disgust.py")
            pass
        elif self.emotion == "neutral":
            emotions.neutral()


class CameraThread(QThread):
    robot = None
    camera_bot = all_gpt.CameraBot()

    prompt = ""

    config_signal = pyqtSignal(float, float, int, float, int)
    track_signal = pyqtSignal(int, int)
    ans_signal = pyqtSignal(str)
    record_signal = pyqtSignal()

    def __init__(self):
        super().__init__()

    def reset_messages(self):
        self.camera_bot.reset_messages()
        # self.add_memory()
        self.ans_signal.emit("System: 已重置CameraBot历史消息！\n")

    def update_prompt(self, prompt):
        self.prompt = prompt

    def run(self):
        if self.robot is not None:
            ans = self.camera_bot.get_answer_context(self.prompt)
            if ans == -1:
                self.ans_signal.emit("System：连接错误！\n")
                return
            if ans == -2:
                self.ans_signal.emit("System：参数无效或账户权限问题！\n")
                return
            try:
                ans_json = json.loads(ans)
                self.ans_signal.emit("CameraBot：" + str(ans_json) + "\n")
                text2audio(ans_json["analysis"])
                self.config_signal.emit(ans_json["camera_config"][0], ans_json["camera_config"][1],
                                        ans_json["camera_config"][2], ans_json["camera_config"][3],
                                        ans_json["camera_config"][4])
                if ans_json["track"]:
                    self.track_signal.emit(ans_json["target_pos"][0], ans_json["target_pos"][1])
                for move in ans_json["move_list"]:
                    self.ans_signal.emit("CameraBot：正在执行动作：\n" + str(move) + "\n")
                    move2point(z=move["z"], pos=move["pos"], speed=move["speed"], t=move["stay_time"])
                self.record_signal.emit()
            except json.decoder.JSONDecodeError:
                self.ans_signal.emit(f"System：返回值非json格式: \n{ans}\n")
        else:
            self.ans_signal.emit("System：请先连接机器人！\n")


def move2point(z, pos, speed, fix_head=True, t=0):
    start_pos = robot.get_joint_position()[1]
    final_pos = start_pos.copy()
    if z == "up":
        final_pos[1:4] = [2 * PI / 3, 0, PI / 3]
    elif z == "mid":
        final_pos[1:4] = [5 * PI / 6, PI / 6, 0]
    elif z == "down":
        final_pos[1:4] = [PI, PI / 6, -PI / 6]
    if pos == "north":
        final_pos[0] = -3 * PI / 4
    elif pos == "south":
        final_pos[0] = PI / 4
    elif pos == "east":
        final_pos[0] = -5 * PI / 4
    elif pos == "west":
        final_pos[0] = -PI / 4
    elif pos == "northeast":
        final_pos[0] = -PI
    elif pos == "southeast":
        final_pos[0] = -3 * PI / 2
    elif pos == "northwest":
        final_pos[0] = -PI / 2
    elif pos == "southwest":
        final_pos[0] = 0
    elif pos == "center":
        if z == "up":
            final_pos[1:4] = [PI / 2, 0, PI / 2]
        # elif z == "mid":
        #     final_pos[1:4] = [2 * PI / 15, 11 * PI / 15, 2 * PI / 15]
    if fix_head:
        d_pos = start_pos[0] - final_pos[0]
        final_pos[4] += d_pos
    robot.joint_move(final_pos, ABS, False, speed)
    while robot.is_in_pos()[1] == 0:
        time.sleep(0.1)
    time.sleep(t)


class AutoThread(QThread):
    enable_auto = False

    input = ""

    prompt_queue = []
    target_id = None
    target_cls = None
    target_gender = None
    target_age = None
    target_emotion = None
    target_pos = None
    target_distance = None
    object_list = []
    arm_pos = None
    arm_is_stuck = None
    memory_list = {"name_list": [], "sentence_list": []}  # 用于存储记忆
    info_request_signal = pyqtSignal()  # 用于请求信息
    ans_signal = pyqtSignal(str)  # 用于输出回答
    photo_signal = pyqtSignal(str)  # 用于拍照
    emotion_signal = pyqtSignal(str)

    a2t_thread = Audio2TextThreadAuto()
    camera_thread = CameraThread()

    def __init__(self, gpt=all_gpt.AutoBot()):
        super().__init__()
        self.auto_bot = gpt

    def generate_input(self):
        input_dict = {
            "prompt": self.prompt_queue,
            "target_id": self.target_id,
            "target_cls": self.target_cls,
            "target_gender": self.target_gender,
            "target_age": self.target_age,
            "target_emotion": self.target_emotion,
            "target_pos": self.target_pos,
            "target_distance": self.target_distance,
            "object_list": self.object_list,
            "arm_pos": self.arm_pos,
            "arm_is_stuck": self.arm_is_stuck,
            "memory_name": self.memory_list["name_list"],
        }
        self.input = str(input_dict)

    def wait_main_thread(self):
        while self.arm_pos is None:
            time.sleep(0.1)

    def run(self):
        self.enable_auto = True
        self.a2t_thread.start()
        while self.enable_auto:
            self.info_request_signal.emit()  # 通知主线程发送画面信息
            self.wait_main_thread()  # 等待主线程完成操作
            self.generate_input()
            p_queue = self.prompt_queue.copy()
            self.ans_signal.emit("Input：" + self.input + "\n")
            ans = self.auto_bot.get_answer_context(self.input)
            if ans == -1:
                self.ans_signal.emit("System：连接错误！\n")
                time.sleep(8)
                continue
            if ans == -2:
                self.ans_signal.emit("System：参数无效或账户权限问题！\n")
                self.reset_messages()
                time.sleep(8)
                continue

            # 解析回答
            try:
                ans_json = json.loads(ans)
                self.ans_signal.emit("AutoBot：" + ans + "\n")

                if ans_json["movie_prompt"] is None and not ans_json["photo"]:
                    self.emotion_signal.emit(ans_json["emotion"])
                if ans_json["photo"]:  # 如果需要拍照
                    self.ans_signal.emit("System：正在拍照...\n")
                    self.photo_signal.emit(ans_json["photo_comments"])
                if ans_json["target_name"] is not None and self.target_id is not None:  # 如果有人物名字
                    name_dict = {"id": self.target_id, "name": ans_json["target_name"]}  # 人物字典
                    if name_dict not in self.memory_list["name_list"]:  # 如果人物不在记忆列表中
                        self.memory_list["name_list"].append(name_dict)  # 添加新的人物
                        self.ans_signal.emit("System：已添加新人物！\n")
                if ans_json["memory_prompt"]:  # 如果记忆对话
                    sentence_dict = {"id": self.target_id, "sentence": p_queue}
                    self.memory_list["sentence_list"].append(sentence_dict)
                    self.ans_signal.emit("System：已添加新回忆！\n")
                text2audio(ans_json["answer"])

                if ans_json["movie_prompt"] is not None:  # 如果需要移动
                    self.ans_signal.emit("AutoBot：CameraBot人格已上线...\n")
                    self.camera_thread.prompt = ans_json["movie_prompt"]
                    self.camera_thread.start()
                    self.camera_thread.wait()
                # self.a2t_thread.terminate()
            except json.decoder.JSONDecodeError:
                self.ans_signal.emit(f"System：返回值非json格式: \n{ans}\n")

            self.a2t_thread.start()
            self.all_reset()  # 重置所有信息
            # self.add_memory()  # 添加记忆
            time.sleep(8)
        self.a2t_thread.terminate()

    def reset_messages(self):
        self.auto_bot.reset_messages()
        # self.add_memory()
        self.ans_signal.emit("System: 已重置AutoBot历史消息！\n")

    #     def add_memory(self):
    #         memory_message = f'''下面是你的记忆内容:
    # 你记住的id和对应的人名: {self.memory_list["name_list"]}
    # 你记住的id和对应id说过的话: {self.memory_list["sentence_list"]}
    # '''
    #         self.auto_bot.messages[0]["content"] += memory_message

    def toggle_a2t(self):
        self.a2t_thread.enable_a2t = not self.a2t_thread.enable_a2t

    def all_reset(self):
        self.input = ""
        self.target_id = None
        self.target_cls = None
        self.target_gender = None
        self.target_age = None
        self.target_emotion = None
        self.target_pos = None
        self.target_distance = None
        self.object_list = []
        self.arm_pos = None
        self.arm_is_stuck = None

    def stop(self):
        self.all_reset()
        self.enable_auto = False
        self.a2t_thread.terminate()
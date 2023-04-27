import os
import time
import openai
import cv2
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QComboBox, QLabel
from PyQt5.QtMultimedia import QCameraInfo
from PyQt5.QtGui import QPainter
from AIDetector_pytorch import Detector
import numpy as np
import speech_recognition as sr
import re
import pyttsx3
import requests
from pocketsphinx import LiveSpeech

PI = 3.1415926
ABS = 0  # 绝对运动
INCR = 1  # 增量运动
Enable = True
Disable = False


class TextLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(30)


class VideoThread(QThread):
    # 硬件相关
    robot = None
    det = Detector()

    # 信号相关
    frame_ready = pyqtSignal(np.ndarray)
    # obj_ready = pyqtSignal(list)
    text_signal = pyqtSignal(str)
    button_signal = pyqtSignal(str)
    target_info_signal = pyqtSignal(list)
    ref_info_signal = pyqtSignal(list)
    resolution_info_signal = pyqtSignal(list)
    robot_position_info_signal = pyqtSignal(list)

    # 追踪器相关
    obj_info = []
    enable = enable_track = enable_record = False
    target_id = 0
    w = h = 0
    rx = ry = 0

    def __init__(self, camera_index=0):
        super().__init__()
        self.camera_index = camera_index
        self.cap = cv2.VideoCapture(self.camera_index)

    def run(self):
        s = time.time()
        self.enable = True
        count = 0
        VideoWriter = None

        while self.enable:
            # start_time = time.time()
            # 读取视频帧
            ret, frame = self.cap.read()
            if not ret:  # 读取失败
                break
            if self.enable_record:
                if VideoWriter is None:
                    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
                    VideoWriter = cv2.VideoWriter('result.mp4', fourcc, 18, (frame.shape[1], frame.shape[0]))
                VideoWriter.write(frame)

            if self.rx == 0:  # 初始化中心点
                self.w = frame.shape[1]
                self.h = frame.shape[0]
                self.rx = frame.shape[1] / 2
                self.ry = 3 * frame.shape[0] / 4
                self.resolution_info_signal.emit([self.w, self.h])
                self.ref_info_signal.emit([self.rx, self.ry])

            # 进行目标检测
            result = self.det.feedCap(frame)
            self.obj_info = result['obj_info']
            self.frame_ready.emit(result['frame'])
            flag = 0
            for obj in self.obj_info:
                if obj[3] == self.target_id:
                    flag = 1
                    ex = obj[0] - self.rx
                    ey = obj[1] - self.ry
                    if ex > 10:
                        x_output = 0.004
                    elif ex < -10:
                        x_output = -0.004
                    else:
                        x_output = 0
                    if ey > 10:
                        y_output = 0.001
                    elif ey < -10:
                        y_output = -0.001
                    else:
                        y_output = 0
                    if self.enable_track and self.robot is not None:
                        self.robot.servo_j(joint_pos=[-0.5*x_output, -y_output, 2 * y_output, -y_output, -x_output, 0], move_mode=1)
                        if count % 10 == 0:
                            robot_joint = self.robot.get_joint_position()
                            if robot_joint[0] == 0:
                                robot_joint = [round(num,2) for num in robot_joint[1]]
                            else:
                                robot_joint = [-1, -1, -1, -1, -1, -1]
                            robot_tcp = self.robot.get_tcp_position()
                            if robot_tcp[0] == 0:
                                robot_tcp = [round(num,2) for num in robot_tcp[1]]
                            else:
                                robot_tcp = [-1, -1, -1, -1, -1, -1]
                            self.robot_position_info_signal.emit([robot_joint, robot_tcp])
                            pass
                    if count % 10 == 0:
                        self.target_info_signal.emit([obj[0], obj[1], obj[2], ex, ey, x_output, y_output])
                    break
            if flag == 0:
                if count % 10 == 0:
                    self.target_info_signal.emit([0, 0, 0, 0, 0, 0, 0])
                pass
            count += 1
            time.sleep(0.04)
            # end_time = time.time()
            # print(end_time-start_time)

        self.rx = self.ry = 0
        self.w = self.h = 0
        e = time.time()
        # print("avr",(e-s)/count)

    def stop(self):
        self.enable = False

    def toggle_track(self):
        self.enable_track = not self.enable_track

    def toggle_record(self):
        self.enable_record = not self.enable_record

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


class VideoLabel(QLabel):
    mouse_signal = pyqtSignal(int, int, int, int)
    painter = QPainter()
    last_point = None

    def __init__(self):
        super().__init__()

    def mousePressEvent(self, event):
        x = event.x()
        y = event.y()
        self.mouse_signal.emit(x, y, self.width(), self.height())
        # if self.last_point is not None:
        #     self.painter.eraseRect(QRect(self.last_point, QSize(5, 5)))
        # self.painter.setPen(QPen(QColor(255, 0, 0), 50))  # 设置画笔颜色和宽度
        # self.painter.drawPoint(x, y)
        # self.last_point = QPoint(x, y)


class Audio2TextThread(QThread):
    text_signal = pyqtSignal(str)

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
            self.text_signal.emit(text)
        except sr.UnknownValueError:
            self.text_signal.emit("无法识别")
        except sr.RequestError as e:
            self.text_signal.emit("请求出错：" + str(e))


class CameraSelector(QComboBox):
    camera_index_signal = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.currentIndexChanged.connect(self.camera_index_signal.emit)
        self.populate()

    def populate(self):
        available_cameras = QCameraInfo.availableCameras()
        self.clear()
        for camera_info in available_cameras:
            self.addItem(camera_info.description())
        if len(available_cameras) == 0:
            self.addItem("没有可用的摄像头")


class GPT:
    key = "APIKEY"
    model = "gpt-3.5-turbo"

    enable_say = True

    text_signal = pyqtSignal(str)

    def __init__(self):
        openai.api_key = self.key
        # self.messages = [
        #     {"role": "system", "content": "You are a helpful assistant."},
        #     {"role": "user", "content": "接下来的回答不要超过30字。"},
        #     {"role": "assistant", "content": "好的，我会尽力遵守您的要求。有什么可以帮您的吗？"},
        # ]
        self.messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user",
             "content": "接下来你需要在代码块里输出我要求的代码，我会把你输出的代码写入已有的程序框架中，并自动运行修改后的程序使机械臂运动。记住：不要导入任何库。不要导入任何库。不要导入任何库。"},
            {"role": "assistant", "content": "好的，我会尽力遵守您的要求。有什么可以帮您的吗？"},
            {"role": "user", "content": "如果是运动控制类的指令，回答请直接输出在程序代码块里，在代码块之外回答'动作执行完毕！'。不要导入任何库。不要导入任何库。不要导入任何库。"
                                        "现在有一个控制机械臂每个关节运动的python函数：robot.joint_move(joint_pos, 1, False, 1)。\n"
                                        "joint_pos: 类型为一个6元素的元组，元组中的每个元素代表机械臂对应关节旋转角度，正数为顺时针，负数为逆时针，单位：rad。\n"
                                        "你只需要按照后面例子的格式进行回答。例子: robot.joint_move((0, PI/2, 0, 0, 0, 0), 1, False, 1)。\n"
                                        "记住：一定要输出程序代码块，然后在代码块之外输出语句'动作执行完毕！'。只要输出程序代码块，然后在代码块之外输出语句'动作执行完毕！'。"
                                        "还有一个控制机械臂运动的python函数：robot.linear_move(end_pos, 1, False, 10)。\n"
                                        "end_pos: 类型为一个6元素的元组(x, y, z, rx, ry, rz)，"
                                        "元组中的每个元素代表向该方向上移动的距离，x向左正向右负，y向前正向后负，z向上正向下负，单位：mm，注意单位的换算。\n"
                                        "你只需要按照后面例子的格式进行回答。例子: robot.linear_move((20, 100, -50, 0, 0, 0), 1, False, 10)。\n"
                                        "如果要求方向是斜向方向，需要用勾股定理计算，例如要求向左下移动20 mm，应输出："
                                        "robot.linear_move((20/math.sqrt(2), 0, -20/math.sqrt(2), 0, 0, 0), 1, False, 10)\n"
                                        "记住：一定要输出程序代码块里，然后在代码块之外输出语句'动作执行完毕！'。只要输出程序代码块，然后在代码块之外输出语句'动作执行完毕！'。"},
            {"role": "assistant", "content": "好的，那么您需要我做什么样的代码呢？"}
        ]

    def get_answer(self, question):
        completion = openai.ChatCompletion.create(
            model=self.model,
            messages=self.messages
        )
        self.input_message(question)
        self.messages.append({"role": "user", "content": question})
        ans = completion.choices[0].message
        self.messages.append(ans)
        return ans.content

    def control_robot(self, question):
        completion = openai.ChatCompletion.create(
            model=self.model,
            messages=self.messages
        )
        self.input_message(question)
        self.messages.append({"role": "user", "content": question})
        ans = completion.choices[0].message
        code = get_code(ans.content)
        if code == "":
            self.messages.append(ans)
            return ans.content
        else:
            self.messages.append({"role": "assistant", "content": "动作执行完毕！"})
            write_code(code)
            flag = os.system("python temp.py")
            if flag != 0:
                return "动作执行失败！"
            elif self.enable_say:   # 机械臂运动完毕后，允许说话，就不输出代码
                return "动作执行完毕！"
            elif not self.enable_say:   # 机械臂运动完毕后，不允许说话，就输出代码
                # ans.content = ans.content.replace("\n", "")
                # ans.content = re.sub(r"(.*)```(.*)```", "", ans.content)
                # self.messages.append(ans)
                return ans.content

    def input_message(self, text):
        message = {"role": "user", "content": text}
        self.messages.append(message)

    def change_key(self, key):
        self.key = key
        openai.api_key = self.key

    def change_model(self, model):
        self.model = model


class GetAnsThread(QThread):
    ans_signal = pyqtSignal(str)
    gpt_signal = pyqtSignal(GPT)

    def __init__(self, question="你好", gpt=GPT()):
        super().__init__()
        self.question = question
        self.gpt = gpt

    def run(self):
        try:
            ans = self.gpt.control_robot(self.question)
            self.ans_signal.emit("System：" + ans + "\n")
            if self.gpt.enable_say:
                text2audio(ans)
            self.gpt_signal.emit(self.gpt)
        except requests.exceptions.ConnectionError:
            self.ans_signal.emit("System：连接错误！\n")
        except openai.error.OpenAIError:
            self.ans_signal.emit("System：参数无效或账户权限问题！\n")

    def toggle_say(self):
        self.gpt.enable_say = not self.gpt.enable_say
        self.ans_signal.emit("System：语音播报已" + ("开启" if self.gpt.enable_say else "关闭") + "！\n")


def get_code(text):
    pattern = re.compile(r"```python(.*?)```", re.S)
    match = pattern.findall(text)
    if match:
        return match[0]
    pattern = re.compile(r"```(.*?)```", re.S)
    match = pattern.findall(text)
    if match:
        return match[0]
    return ""


def write_code(code):
    with open("example.txt", "r") as f:
        example = f.read()
    code = example.replace("# replace the text", code)
    with open("temp.py", "w") as f:
        f.write(code)


class RecordThread(QThread):
    enable_record = False

    def __int__(self, camera_index=0):
        super().__init__()
        self.camera_index = camera_index
        self.cap = cv2.VideoCapture(self.camera_index)

    def run(self):
        VideoWriter = None
        while self.enable_record:
            ret, im = self.cap.read()
            if not ret:  # 读取失败
                break
            if VideoWriter is None:
                fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
                videoWriter = cv2.VideoWriter('result.mp4', fourcc, 30, (im.shape[1], im.shape[0]))
            VideoWriter.write(im)
            time.sleep(0.33)

    def stop(self):
        self.enable_record = False


class WakeThread(QThread):
    enable_wake = False

    text_signal = pyqtSignal(str)
    gpt_signal = pyqtSignal(GPT)

    def __init__(self, question="你好", gpt=GPT()):
        super().__init__()
        self.question = question
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
                        break
                    answer = self.gpt.control_robot(self.question)
                    self.text_signal.emit("System: " + answer + "\n")
                    self.gpt_signal.emit(self.gpt)
                    text2audio(answer)
                if flag:
                    break

    def stop(self):
        self.enable_wake = False

    def audio2text(self):
        # 创建语音识别对象
        r = sr.Recognizer()
        # 使用麦克风录制语音
        with sr.Microphone() as source:
            self.text_signal.emit("System: 请说话...\n")
            audio = r.listen(source)
        # 将语音转换为文本
        try:
            text = r.recognize_google(audio, language='zh-CN')
            self.text_signal.emit("User: " + text + "\n")
            return text
        except sr.UnknownValueError:
            self.text_signal.emit("System: 无法识别语音!请重试！\n")
            text2audio("无法识别语音!请重试！")
            return -1
        except sr.RequestError as e:
            self.text_signal.emit("System: 请求出错：" + str(e) + "\n")
            text2audio("请求出错!请重试！")
            return -1


def text2audio(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


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

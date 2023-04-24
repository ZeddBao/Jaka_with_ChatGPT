import cv2
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QLabel, QMainWindow, QSplitter, QTextEdit, QVBoxLayout, QWidget, \
    QLineEdit, QPushButton, QScrollArea
from AIDetector_pytorch import Detector
import numpy as np
import speech_recognition as sr


class VideoThread(QThread):
    frame_ready = pyqtSignal(np.ndarray)
    obj_ready = pyqtSignal(list)
    det = Detector()
    obj_info = []
    enable = False
    enable_info = False

    def __init__(self, parent=None):
        super().__init__(parent)
        self.cap = cv2.VideoCapture(0)
        self.det = Detector()

    def run(self):
        self.enable = True
        while self.enable:
            ret, frame = self.cap.read()
            if not ret:
                break
            result = self.det.feedCap(frame)
            self.obj_info = result['obj_info']
            if self.enable_info:
                self.obj_ready.emit(result['obj_info'])
            self.frame_ready.emit(result['frame'])

    def stop(self):
        self.enable = False

    def toggle_info(self):
        self.enable_info = not self.enable_info


# 这里，我们创建了一个新的 frame_ready 信号，用于在新线程中发射帧数据。run 函数中，我们使用 cv2.VideoCapture 读取帧，然后发送帧数据到主线程。
# 接下来，在主窗口类中，我们需要修改 __init__ 函数，将 QTimer 替换为我们刚刚创建的新线程类：

class MyWindow(QMainWindow):
    target_id = 0
    line_temp = ""

    # det = Detector()

    def __init__(self):
        super().__init__()

        # 创建 QLabel 控件，并将其添加到布局中
        self.video = QLabel(self)
        self.video.setScaledContents(True)  # 设置 scaledContents 属性

        # 创建 QTextEdit 控件并设置一些初始文本
        self.text_edit = QTextEdit(self)
        self.text_edit.setPlainText("这是一个聊天对话窗口。")

        # 将 QTextEdit 控件包含在 QScrollArea 控件中
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)  # 设置 widgetResizable 属性
        self.scroll_area.setWidget(self.text_edit)

        # 创建 QLineEdit 和 QPushButton 控件
        self.line_edit = QLineEdit()
        self.send_button = QPushButton("发送")
        self.audio_button = QPushButton("语音")

        self.camera_button = QPushButton("打开/关闭摄像头")
        self.display_obj_button = QPushButton("检测物体信息")
        self.choose_button = QPushButton("选择目标ID")
        self.display_target_button = QPushButton("目标信息")
        self.clear_button = QPushButton("清空记录")

        layout0 = QHBoxLayout()
        layout0.addWidget(self.camera_button)
        layout0.addWidget(self.display_obj_button)
        layout0.addWidget(self.choose_button)
        layout0.addWidget(self.display_target_button)
        layout0.addWidget(self.clear_button)

        # 创建 QHBoxLayout 布局，并将 QLineEdit 和 QPushButton 控件添加到其中
        layout1 = QHBoxLayout()
        layout1.addWidget(self.line_edit)
        layout1.addWidget(self.send_button)
        layout1.addWidget(self.audio_button)

        # 创建 QWidget 控件，并将 QSplitter 和 QHBoxLayout 添加到其中
        splitter = QSplitter()
        splitter.addWidget(self.video)
        splitter.addWidget(self.scroll_area)
        splitter.setSizes([640, 320])  # 设置每个部分的初始大小

        widget = QWidget()
        v_layout = QVBoxLayout()
        v_layout.addWidget(splitter)
        v_layout.addLayout(layout0)
        v_layout.addLayout(layout1)
        widget.setLayout(v_layout)

        # 将 QWidget 控件设置为应用程序的中心窗口部件
        self.setCentralWidget(widget)

        # 创建一个新的线程来读取视频帧
        self.video_thread = VideoThread(self)
        self.video_thread.frame_ready.connect(self.update_frame)
        self.video_thread.obj_ready.connect(self.update_obj)
        # 设置定时器并启动
        # self.timer = QTimer(self)
        # self.timer.timeout.connect(self.update_text)
        # self.timer.start(1000)

        # 将 QPushButton 控件的 clicked 信号连接到槽函数 send_message
        self.send_button.clicked.connect(self.send_message)
        self.line_edit.returnPressed.connect(self.send_message)
        self.camera_button.clicked.connect(self.toggle_camera)
        self.display_obj_button.clicked.connect(self.display_obj_info)
        self.choose_button.clicked.connect(self.ask_id)
        self.display_target_button.clicked.connect(self.display_target_info)
        self.clear_button.clicked.connect(self.clear_record)
        self.audio_button.clicked.connect(self.google_a2t)

    def google_a2t(self):  # 考虑使用多进程
        # 创建语音识别对象
        r = sr.Recognizer()
        # 使用麦克风录制语音
        with sr.Microphone() as source:
            audio = r.listen(source)

        # 将语音转换为文本
        try:
            text = r.recognize_google(audio, language='zh-CN')
            self.line_edit.setText(text)
            self.line_edit.setFocus()
        except sr.UnknownValueError:
            self.line_edit.setText("抱歉，无法识别你的语音")
            self.line_edit.setFocus()
        except sr.RequestError as e:
            self.line_edit.setText("请求出错：" + str(e))
            self.line_edit.setFocus()

    def update_frame(self, frame):
        # 将 OpenCV 图像转换为 QImage 对象
        height, width, channel = frame.shape
        bytesPerLine = channel * width
        qImg = QImage(frame.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()

        # 将 QImage 对象设置为 QLabel 控件的图像
        pixmap = QPixmap.fromImage(qImg)
        self.video.setPixmap(pixmap)

    def update_obj(self, obj_info):
        text = "System:\n"
        for obj in obj_info:
            text += "id：" + str(obj[3]) + "    坐标：(" + str(obj[0]) + "," + str(obj[1]) + ")    面积：" + str(
                obj[2]) + "\n"
        self.text_edit.append(text)

    def toggle_camera(self):
        if not self.video_thread.isRunning():
            self.video_thread.start()
            self.camera_button.setText("关闭摄像头")
        else:
            self.video_thread.stop()
            self.video_thread.wait()
            self.camera_button.setText("打开摄像头")

    def display_obj_info(self):
        text = "System:\n"
        for obj in self.video_thread.obj_info:
            text += "id：" + str(obj[3]) + "    坐标：(" + str(obj[0]) + "," + str(obj[1]) + ")    面积：" + str(
                obj[2]) + "\n"
        self.text_edit.append(text)

    def display_target_info(self):
        text = "System:\n"
        flag = False
        for obj in self.video_thread.obj_info:
            if obj[3] == self.target_id:
                text += "id：" + str(obj[3]) + "    坐标：(" + str(obj[0]) + "," + str(obj[1]) + ")    面积：" + str(
                    obj[2]) + "\n"
                flag = True
                break
        if not flag:
            self.text_edit.append("System: 失去目标！\n")
        else:
            self.text_edit.append(text)

    # def toggle_obj_info(self):
    #     self.video_thread.toggle_info()

    def ask_id(self):
        if self.video_thread.enable:
            self.toggle_camera()
        self.text_edit.append("System: 请选择目标ID！输入'cancel'取消！\n")
        self.line_edit.setFocus()
        self.send_button.clicked.connect(self.choose_id)
        self.line_edit.returnPressed.connect(self.choose_id)

    def choose_id(self):

        if self.line_temp == "cancel":
            self.text_edit.append("System: 取消选择！\n")
            self.send_button.clicked.disconnect(self.choose_id)
            self.line_edit.returnPressed.disconnect(self.choose_id)
            self.toggle_camera()
            return
        elif not self.line_temp.isnumeric():
            self.text_edit.append("System: 请输入数字ID！重新选择或输入'cancel'取消！\n")
            self.line_edit.setFocus()
            return
        elif int(self.line_temp) not in [obj[3] for obj in self.video_thread.obj_info]:
            self.text_edit.append("System: ID不存在！重新选择或输入'cancel'取消！\n")
            self.line_edit.setFocus()
            return

        self.target_id = int(self.line_temp)
        self.text_edit.append("System: 目标ID为" + str(self.target_id) + "！\n")
        self.toggle_camera()
        self.send_button.clicked.disconnect(self.choose_id)
        self.line_edit.returnPressed.disconnect(self.choose_id)

    def clear_record(self):
        self.text_edit.clear()

    def send_message(self):
        # 从 QLineEdit 控件中读取文本
        text = self.line_edit.text()
        self.line_temp = text
        # 将文本显示在 QTextEdit 控件中
        self.text_edit.append("User：" + text + "\n")
        # 清空 QLineEdit 控件中的文本
        self.line_edit.clear()


if __name__ == '__main__':
    app = QApplication([])
    window = MyWindow()
    window.show()
    app.exec_()

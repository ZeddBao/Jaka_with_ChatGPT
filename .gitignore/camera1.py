import cv2
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QLabel, QMainWindow, QSplitter, QTextEdit, QVBoxLayout, QWidget, \
    QLineEdit, QPushButton, QScrollArea
from AIDetector_pytorch import Detector


class MyWindow(QMainWindow):
    obj_info = []

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

        self.camera_button = QPushButton("打开/关闭摄像头")
        self.display_obj_button = QPushButton("展示检测物体信息")
        self.choose_button = QPushButton("选择目标ID")
        self.clear_button = QPushButton("清空记录")

        layout0 = QHBoxLayout()
        layout0.addWidget(self.camera_button)
        layout0.addWidget(self.display_obj_button)
        layout0.addWidget(self.choose_button)
        layout0.addWidget(self.clear_button)

        # 创建 QHBoxLayout 布局，并将 QLineEdit 和 QPushButton 控件添加到其中
        layout1 = QHBoxLayout()
        layout1.addWidget(self.line_edit)
        layout1.addWidget(self.send_button)

        # 创建 QWidget 控件，并将 QSplitter 和 QHBoxLayout 添加到其中
        splitter = QSplitter()
        splitter.addWidget(self.video)
        splitter.addWidget(self.scroll_area)
        splitter.setSizes([600, 400])  # 设置每个部分的初始大小

        widget = QWidget()
        v_layout = QVBoxLayout()
        v_layout.addWidget(splitter)
        v_layout.addLayout(layout0)
        v_layout.addLayout(layout1)
        widget.setLayout(v_layout)

        # 将 QWidget 控件设置为应用程序的中心窗口部件
        self.setCentralWidget(widget)

        # 创建 QTimer 对象，用于定期从摄像头中读取帧
        self.timer = QTimer()
        self.timer.timeout.connect(self.display_frame)
        self.timer.start(20)  # 20ms

        self.detector = Detector()
        # 创建 cv2.VideoCapture 对象
        self.cap = cv2.VideoCapture(0)

        ############################################################################################################

        # 为 QPushButton 控件绑定槽函数
        self.send_button.clicked.connect(self.add_text_to_chat)
        self.camera_button.clicked.connect(self.toggle_camera)
        self.line_edit.returnPressed.connect(self.add_text_to_chat)
        self.clear_button.clicked.connect(self.clear_chat)
        self.display_obj_button.clicked.connect(self.display_obj)

    def add_text_to_chat(self):
        # 获取 QLineEdit 控件的文本
        text = "User: " + self.line_edit.text() + "\n"

        # 将文本添加到 QTextEdit 控件中
        self.text_edit.append(text)

        # 清空 QLineEdit 控件
        self.line_edit.clear()

    def toggle_camera(self):
        if self.timer.isActive():
            self.timer.stop()
            self.cap.release()
        else:
            self.cap = cv2.VideoCapture(0)
            self.timer.start(20)

    def clear_chat(self):
        self.text_edit.clear()

    def choose_obj(self):
        pass

    def display_obj(self):
        self.text_edit.append("System:")
        # for obj in self.obj_info:
        #     text = "id：", obj[3], "    坐标：(", obj[0], ",", obj[1], ")    面积：", obj[2]
        #     self.text_edit.append(text)
        self.text_edit.append("\n")

    def display_frame(self):
        # 从摄像头中读取帧
        _, result = self.cap.read()
        result = self.detector.feedCap(result)
        self.obj_info = result['obj_info']
        result = result['frame']

        # 将 OpenCV 图像转换为 QImage 对象
        height, width, channel = result.shape
        bytesPerLine = channel * width
        qImg = QImage(result.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()

        # 将 QImage 对象设置为 QLabel 控件的图像
        pixmap = QPixmap.fromImage(qImg)
        self.video.setPixmap(pixmap)


if __name__ == '__main__':
    app = QApplication([])
    window = MyWindow()
    window.show()
    app.exec_()

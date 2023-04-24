import cv2
from AIDetector_pytorch import Detector
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QLabel, QMainWindow, QScrollArea, QTextEdit, QVBoxLayout, \
    QWidget, QLineEdit, QPushButton, QSplitter


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 创建 QLabel 控件，并将其添加到布局中
        self.video = QLabel(self)
        self.video.setScaledContents(True)  # 设置 scaledContents 属性
        self.text_edit = QTextEdit(self)
        self.text_edit.setPlainText("这是一个聊天对话窗口。")
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)  # 设置 widgetResizable 属性
        self.scroll_area.setWidget(self.text_edit)
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

        layout1 = QHBoxLayout()
        layout1.addWidget(self.line_edit)
        layout1.addWidget(self.send_button)

        splitter = QSplitter()
        splitter.addWidget(self.video)
        splitter.addWidget(self.scroll_area)
        splitter.setSizes([800, 400])

        widget = QWidget()
        v_layout = QVBoxLayout()
        v_layout.addWidget(splitter)
        v_layout.addLayout(layout0)
        v_layout.addLayout(layout1)
        widget.setLayout(v_layout)

        self.setCentralWidget(widget)

        # 创建 cv2.VideoCapture 对象
        self.cap = cv2.VideoCapture(0)
        self.det = Detector()

        # 创建 QTimer 对象，用于定期从摄像头中读取帧
        self.timer = QTimer()
        self.timer.timeout.connect(self.display_frame)
        self.timer.start(30)  # 每秒显示 60 帧

    def display_frame(self):
        # 从摄像头中读取帧
        ret, frame = self.cap.read()
        if not ret:
            return
        result = self.det.feedCap(frame)
        obj_info = result['obj_info']
        result = result['frame']

        # 将 OpenCV 图像转换为 QImage 对象
        rgb_image = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)

        # 将 QImage 对象设置为 QLabel 控件的图像
        pixmap = QPixmap.fromImage(qt_image)
        self.video.setPixmap(pixmap)


if __name__ == '__main__':
    app = QApplication([])
    window = MyWindow()
    window.show()
    app.exec_()

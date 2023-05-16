from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QComboBox, QLabel
from PyQt5.QtMultimedia import QCameraInfo
from PyQt5.QtGui import QPainter
import pyttsx3

PI = 3.1415926
ABS = 0  # 绝对运动
INCR = 1  # 增量运动
Enable = True
Disable = False


class TextLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(30)


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


def text2audio(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

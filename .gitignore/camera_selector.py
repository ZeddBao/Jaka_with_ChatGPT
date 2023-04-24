from PyQt5.QtWidgets import QComboBox
from PyQt5.QtMultimedia import QCameraInfo
from PyQt5 import QtCore


class CameraSelector(QComboBox):
    camera_index = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.currentIndexChanged.connect(self.camera_index.emit)
        self.populate()


    def populate(self):
        available_cameras = QCameraInfo.availableCameras()

        for camera_info in available_cameras:
            self.addItem(camera_info.description())

        if len(available_cameras) == 0:
            self.addItem("没有可用的摄像头")



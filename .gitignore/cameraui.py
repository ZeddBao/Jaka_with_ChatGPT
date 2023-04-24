from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from camera_selector import CameraSelector


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Camera Selector Example")

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.camera_selector = CameraSelector()
        self.camera_selector.camera_index.connect(self.on_camera_selected)
        layout.addWidget(self.camera_selector)

        self.label = QLabel("No camera selected")
        layout.addWidget(self.label)

    def on_camera_selected(self, camera_info):
        self.label.setText(f"Selected camera: {camera_info}")


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()

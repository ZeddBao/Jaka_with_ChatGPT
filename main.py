import cv2
import openai
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QMainWindow, QSplitter, QTextEdit, QVBoxLayout, QWidget, \
    QLineEdit, QPushButton, QScrollArea, QSpinBox, QComboBox, QLabel, QTabWidget
import jkrc
import track_widgets as tw
import os
import all_gpt
import all_thread
from deepface import DeepFace
import numpy as np
import datetime

openai.api_key = os.getenv("OPENAI_API_KEY")
robot = jkrc.RC("10.5.5.100")
PI = 3.1415926
ABS = 0  # 绝对运动
INCR = 1  # 增量运动
Enable = True
Disable = False


class MainWindow(QMainWindow):
    robot = None
    GPT = all_gpt.GPT()

    target_id = 0
    line_temp = []

    enable_GPT = True
    enable_camera_thread = False

    def __init__(self):
        super().__init__()
        self.setWindowTitle("行影控制界面")

        # 创建视频和聊天窗口
        self.video = tw.VideoLabel()
        self.video.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.video.setBaseSize(1280, 960)
        self.video.setScaledContents(True)  # 设置 scaledContents 属性
        self.text_edit = QTextEdit()
        self.text_edit.setPlainText("这是一个聊天对话窗口。")
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)  # 设置 widgetResizable 属性
        self.scroll_area.setWidget(self.text_edit)
        self.scroll_area.setBaseSize(960, 960)

        # 创建消息输入相关控件
        self.wake_button = QPushButton("打开/关闭唤醒模式")
        self.GPT_button = QPushButton("开启/关闭GPT")
        self.line_edit = QLineEdit()
        self.send_button = QPushButton("发送")
        self.audio_button = QPushButton("语音")
        self.say_button = QPushButton("打开/关闭语音播报")
        self.clear_button = QPushButton("清空记录")

        # 创建硬件相关控件
        self.robot_ip_line = QLineEdit("10.5.5.100")
        self.robot_enable_button = QPushButton("连接机器人")
        self.robot_disable_button = QPushButton("断开机器人")
        self.camera_selector = tw.CameraSelector()
        self.camera_refresh_button = QPushButton("刷新")
        self.camera_button = QPushButton("打开/关闭摄像头")
        self.record_button = QPushButton("REC")

        # 创建硬件信息相关控件
        self.arm_joint_info1 = tw.TextLabel("关节角度：")
        self.arm_joint_info2 = tw.TextLabel()
        self.arm_pose_info1 = tw.TextLabel("末端位姿：")
        self.arm_pose_info2 = tw.TextLabel()
        self.camera_resolution_info1 = tw.TextLabel("分辨率：")
        self.camera_resolution_info2 = tw.TextLabel()

        # 创建追踪信息相关控件
        self.target_position_info1 = tw.TextLabel("目标坐标：")
        self.target_position_info2 = tw.TextLabel()
        self.target_size_info1 = tw.TextLabel("目标大小：")
        self.target_size_info2 = tw.TextLabel()
        self.ref_position_info1 = tw.TextLabel("参考点坐标：")
        self.ref_position_info2 = tw.TextLabel()
        self.err_info1 = tw.TextLabel("误差像素：")
        self.err_info2 = tw.TextLabel()
        self.output_info1 = tw.TextLabel("步进长度：")
        self.output_info2 = tw.TextLabel()

        # 创建追踪相关控件
        self.display_obj_button = QPushButton("检测物体信息")
        self.id_input_box = QSpinBox()
        self.id_input_box.setMaximum(9999)
        self.id_input_box.setValue(1)
        self.choose_button = QPushButton("选择目标ID")
        self.track_button = QPushButton("开始/停止跟踪")

        # 创建模式相关控件
        self.mode_label = QLabel("智能模式选择：")
        self.mode_combo = QComboBox(self)
        self.mode_combo.addItem("普通模式")
        self.mode_combo.addItem("半自动模式")
        self.mode_combo.addItem("全自动模式")
        self.current_mode = QLabel("当前模式：普通模式")
        self.reset_bot_button = QPushButton("重置Bot")
        self.auto_a2t_button = QPushButton("打开/关闭语音接收")
        self.track_mode_label = QLabel("追踪模式选择：")
        self.track_combo = QComboBox(self)
        self.track_combo.addItem("自选目标")
        self.track_combo.addItem("随机模式")
        self.track_combo.addItem("丢失随机模式")
        self.track_combo.addItem("注意力模式")
        self.track_combo.addItem("丢失注意力模式")
        self.current_track_mode = QLabel("当前追踪模式：自选目标")

        ############################################################################################################

        # 创建硬件相关控件
        hardware_bar = QHBoxLayout()
        hardware_bar.addWidget(self.robot_ip_line)
        hardware_bar.addWidget(self.robot_enable_button)
        hardware_bar.addWidget(self.robot_disable_button)
        hardware_bar.addWidget(self.camera_selector)
        hardware_bar.addWidget(self.camera_refresh_button)
        hardware_bar.addWidget(self.camera_button)
        hardware_bar.addWidget(self.record_button)

        # 创建硬件信息相关控件
        hardware_info_bar_layout = QHBoxLayout()
        hardware_info_bar_layout.addWidget(self.arm_joint_info1)
        hardware_info_bar_layout.addWidget(self.arm_joint_info2)
        hardware_info_bar_layout.addWidget(self.arm_pose_info1)
        hardware_info_bar_layout.addWidget(self.arm_pose_info2)
        hardware_info_bar_layout.addWidget(self.camera_resolution_info1)
        hardware_info_bar_layout.addWidget(self.camera_resolution_info2)

        # 创建追踪信息相关控件
        track_info_bar_layout = QHBoxLayout()
        track_info_bar_layout.addWidget(self.target_position_info1)
        track_info_bar_layout.addWidget(self.target_position_info2)
        track_info_bar_layout.addWidget(self.target_size_info1)
        track_info_bar_layout.addWidget(self.target_size_info2)
        track_info_bar_layout.addWidget(self.ref_position_info1)
        track_info_bar_layout.addWidget(self.ref_position_info2)
        track_info_bar_layout.addWidget(self.err_info1)
        track_info_bar_layout.addWidget(self.err_info2)
        track_info_bar_layout.addWidget(self.output_info1)
        track_info_bar_layout.addWidget(self.output_info2)

        # 创建追踪相关控件
        track_bar_layout = QHBoxLayout()
        track_bar_layout.addWidget(self.display_obj_button)
        track_bar_layout.addWidget(self.id_input_box)
        track_bar_layout.addWidget(self.choose_button)
        track_bar_layout.addWidget(self.track_button)

        # 创建消息输入相关控件
        message_bar_layout = QHBoxLayout()
        message_bar_layout.addWidget(self.wake_button)
        message_bar_layout.addWidget(self.GPT_button)
        message_bar_layout.addWidget(self.line_edit)
        message_bar_layout.addWidget(self.send_button)
        message_bar_layout.addWidget(self.audio_button)
        message_bar_layout.addWidget(self.say_button)
        message_bar_layout.addWidget(self.clear_button)

        # 创建模式相关控件
        mode_bar_layout = QVBoxLayout()
        lay1 = QVBoxLayout()
        lay1.addWidget(self.mode_label)
        lay1.addWidget(self.mode_combo)
        lay1.addWidget(self.current_mode)
        lay1_widget = QWidget()
        lay1_widget.setLayout(lay1)
        lay1_widget.setStyleSheet("border:1px solid grey;")  # 设置边框
        lay2 = QVBoxLayout()
        lay2.addWidget(self.track_mode_label)
        lay2.addWidget(self.track_combo)
        lay2.addWidget(self.current_track_mode)
        lay2_widget = QWidget()
        lay2_widget.setLayout(lay2)
        lay2_widget.setStyleSheet("border:1px solid grey;")  # 设置边框
        mode_bar_layout.addWidget(lay1_widget)
        mode_bar_layout.addWidget(self.reset_bot_button)
        mode_bar_layout.addWidget(self.auto_a2t_button)
        mode_bar_layout.addWidget(lay2_widget)
        mode_bar_widget = QWidget()
        mode_bar_widget.setLayout(mode_bar_layout)

        # 创建视频和聊天窗口的水平分割器
        splitter = QSplitter()
        splitter.addWidget(mode_bar_widget)
        splitter.addWidget(self.video)
        splitter.addWidget(self.scroll_area)
        splitter.setSizes([160, 640, 320])  # 设置每个部分的初始大小

        # 创建主窗口的垂直布局
        main = QWidget()
        main_layout = QVBoxLayout()
        main_layout.addLayout(hardware_bar)
        main_layout.addLayout(hardware_info_bar_layout)
        main_layout.addWidget(splitter)
        main_layout.addLayout(track_info_bar_layout)
        main_layout.addLayout(track_bar_layout)
        main_layout.addLayout(message_bar_layout)
        main.setLayout(main_layout)  # 设置窗口的布局
        self.setCentralWidget(main)  # 设置窗口的中心部件

        ############################################################################################################

        # 创建一个新的线程来读取视频帧
        self.video_thread = all_thread.VideoThread()
        self.video_thread.frame_ready.connect(self.update_frame)
        self.video_thread.robot_position_info_signal.connect(self.update_robot_position_info)
        self.video_thread.target_info_signal.connect(self.update_target_info)
        self.video_thread.ref_info_signal.connect(self.update_ref_info)
        self.video_thread.resolution_info_signal.connect(self.update_resolution_info)
        self.video_thread.text_signal.connect(self.text_edit.append)
        self.video_thread.button_signal.connect(self.camera_button.setText)

        # 创建一个新的线程来读取语音
        self.audio2text_thread = all_thread.Audio2TextThread()
        self.audio2text_thread.text_signal.connect(self.line_edit.setText)

        # 创建一个新的线程来获取GPT回答
        self.get_gpt_answer_thread = all_thread.GetAnsThread(gpt=self.GPT)
        self.get_gpt_answer_thread.ans_signal.connect(self.text_edit.append)
        self.get_gpt_answer_thread.gpt_signal.connect(self.update_gpt)

        # 创建一个新的线程来录像
        # self.record_thread = tw.RecordThread()

        # 创建一个新的线程语音唤醒
        self.wake_thread = all_thread.WakeThreadNormal(gpt=self.GPT)
        self.wake_thread.ans_signal.connect(self.text_edit.append)
        self.wake_thread.gpt_signal.connect(self.update_gpt)

        # 创建一个新的线程生成全自动机械臂
        self.auto_thread = all_thread.AutoThread()
        self.auto_thread.ans_signal.connect(self.text_edit.append)
        self.auto_thread.info_request_signal.connect(self.update_auto_info)
        self.auto_thread.photo_signal.connect(self.video_thread.save_photo)
        self.auto_thread.a2t_thread.ans_signal.connect(self.text_edit.append)
        self.auto_thread.a2t_thread.ans_signal.connect(self.text_edit.append)
        self.auto_thread.a2t_thread.ans_signal.connect(self.line_temp.append)
        self.auto_thread.emotion_signal.connect(self.move_emotion)

        # 创建一个新的线程来完成表情
        self.emotion_thread = all_thread.EmotionThread()

        # 创建一个新的线程来完成机械臂控制和拍照
        self.camera_thread = all_thread.CameraThread()
        self.camera_thread.config_signal.connect(self.toggle_record)
        self.camera_thread.track_signal.connect(self.update_ref)
        self.camera_thread.track_signal.connect(self.enable_track)
        self.camera_thread.ans_signal.connect(self.text_edit.append)
        self.camera_thread.record_signal.connect(self.toggle_record)

        self.auto_thread.camera_thread.config_signal.connect(self.toggle_record)
        self.auto_thread.camera_thread.track_signal.connect(self.update_ref)
        self.auto_thread.camera_thread.track_signal.connect(self.enable_track)
        self.auto_thread.camera_thread.ans_signal.connect(self.text_edit.append)
        self.auto_thread.camera_thread.record_signal.connect(self.toggle_record)

        ############################################################################################################

        # 连接信号和槽
        self.wake_button.clicked.connect(self.toggle_wake)
        self.GPT_button.clicked.connect(self.toggle_gpt)
        self.send_button.clicked.connect(self.send_message)
        self.line_edit.returnPressed.connect(self.send_message)
        self.audio_button.clicked.connect(self.audio2text)
        self.say_button.clicked.connect(self.get_gpt_answer_thread.toggle_say)
        self.clear_button.clicked.connect(self.clear_record)

        self.robot_enable_button.clicked.connect(self.enable_robot)
        self.robot_disable_button.clicked.connect(self.disable_robot)
        self.camera_selector.camera_index_signal.connect(self.change_camera)
        self.camera_refresh_button.clicked.connect(self.refresh_camera)
        self.camera_button.clicked.connect(self.toggle_camera)
        self.record_button.clicked.connect(lambda: self.toggle_record(ci=33, fps=30, hd=0, sf=1, vd=0))

        self.display_obj_button.clicked.connect(self.display_obj_info)
        self.choose_button.clicked.connect(self.select_id)
        self.track_button.clicked.connect(self.toggle_track)

        self.video.mouse_signal.connect(self.update_ref)

        self.get_gpt_answer_thread.cmd_signal.connect(self.cmd_executor)
        self.wake_thread.cmd_signal.connect(self.cmd_executor)

        self.mode_combo.currentIndexChanged.connect(self.change_mode)
        self.track_combo.currentIndexChanged.connect(self.change_track)
        self.reset_bot_button.clicked.connect(self.auto_thread.reset_messages)
        self.reset_bot_button.clicked.connect(self.camera_thread.reset_messages)
        self.reset_bot_button.clicked.connect(self.auto_thread.camera_thread.reset_messages)
        self.auto_a2t_button.clicked.connect(self.toggle_auto_a2t)

        ############################################################################################################

    # 使能机器人
    def enable_robot(self):
        ip = self.robot_ip_line.text()
        self.robot = jkrc.RC(str(ip))  # 返回一个机器人对象
        self.robot.login()  # 登录
        self.robot.power_on()  # 上电
        self.robot.enable_robot()
        self.robot.motion_abort()
        self.robot.collision_recover()
        self.robot.clear_error()
        # self.robot.servo_move_enable(True)
        self.video_thread.robot = self.robot
        self.camera_thread.robot = self.robot
        self.auto_thread.camera_thread.robot = self.robot
        self.robot.joint_move((-PI * 3 / 4, PI / 3, PI / 3, PI * 1 / 3, -PI / 2, PI / 4), ABS, False, 1)  # default
        self.robot.joint_move((0, -PI / 5, 2 * PI / 5, -PI / 5, 0, 0), INCR, False, 1)  # default
        self.text_edit.append("System: 机器人已连接！\n")
        self.target_id = 0
        self.video_thread.target_id = 0
        self.video_thread.cap_interval = 33
        self.video_thread.hd = self.video_thread.vd = 0
        self.video_thread.sf = 1

    # 断开机器人
    def disable_robot(self):
        if self.robot is not None:
            self.robot.logout()
            self.robot = None
            self.text_edit.append("System: 机器人已断开！\n")
        else:
            self.text_edit.append("System: 机器人未连接！\n")

    # 更新视频帧
    def update_frame(self, frame):
        # 将 OpenCV 图像转换为 QImage 对象
        height, width, channel = frame.shape
        bytesPerLine = channel * width
        qImg = QImage(frame.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()

        # 将 QImage 对象设置为 QLabel 控件的图像
        pixmap = QPixmap.fromImage(qImg)
        self.video.setPixmap(pixmap)

    # 打开/关闭摄像头
    def toggle_camera(self):
        if not self.video_thread.isRunning():
            self.video_thread.start()
            self.camera_button.setText("关闭摄像头")
            self.text_edit.append("System: 摄像头已打开！\n")
        else:
            self.video_thread.stop()
            self.video_thread.wait()
            self.camera_button.setText("打开摄像头")
            self.text_edit.append("System: 摄像头已关闭！\n")

    # 切换摄像头
    def change_camera(self, index):
        self.video_thread.stop()
        self.video_thread.wait()
        self.camera_button.setText("打开摄像头")
        self.video_thread.cap.release()
        self.video_thread.camera_index = index
        self.video_thread.cap = cv2.VideoCapture(index)

    # 刷新摄像头
    def refresh_camera(self):
        self.video_thread.stop()
        self.video_thread.wait()
        self.video_thread.cap.release()
        self.video_thread.cap = cv2.VideoCapture(self.video_thread.camera_index)

    def update_robot_position_info(self, robot_position_info):
        self.arm_joint_info2.setText(
            str(robot_position_info[0][0]) + ", " + str(robot_position_info[0][1]) + ", " + str(
                robot_position_info[0][2]) + ", " + str(robot_position_info[0][3]) + ", " + str(
                robot_position_info[0][4]) + ", " + str(robot_position_info[0][5]))
        self.arm_pose_info2.setText(str(robot_position_info[1][0]) + ", " + str(robot_position_info[1][1]) + ", " + str(
            robot_position_info[1][2]) + ", " + str(robot_position_info[1][3]) + ", " + str(
            robot_position_info[1][4]) + ", " + str(robot_position_info[1][5]))

    # 更新目标信息
    def update_target_info(self, target_info):
        self.target_position_info2.setText(str(target_info[0]) + ", " + str(target_info[1]))
        self.target_size_info2.setText(str(target_info[2]))
        self.err_info2.setText(str(target_info[3]) + ", " + str(target_info[4]))
        self.output_info2.setText(str(target_info[5]) + ", " + str(target_info[6]))

    def update_ref_info(self, ref_info):
        self.ref_position_info2.setText(str(ref_info[0]) + ", " + str(ref_info[1]))

    def update_resolution_info(self, resolution_info):
        self.camera_resolution_info2.setText(str(resolution_info[0]) + ", " + str(resolution_info[1]))

    def update_ref(self, x, y, w=640, h=480):
        self.video_thread.update_ref(x, y, w, h)
        self.text_edit.append("System: 参考点坐标已更新！\n")

    # 显示所有物体信息
    def display_obj_info(self):
        if not self.video_thread.obj_info:
            self.text_edit.append("System: 未检测到物体！\n")
            return
        text = "System:\n"
        for obj in self.video_thread.obj_info:
            text += "id：" + str(obj[3]) + "    坐标：(" + str(obj[0]) + "," + str(obj[1]) + ")    面积：" + str(
                obj[2]) + "\n"
        self.text_edit.append(text)
        pass

    def enable_track(self):
        if not self.video_thread.enable:
            self.text_edit.append("System: 请开启摄像头！\n")
            return
        elif self.video_thread.robot is None:
            self.text_edit.append("System: 请先连接机器人!\n")
            return
        elif self.video_thread.target_id == 0:
            if self.video_thread.attention_id != 0:
                self.video_thread.target_id = self.video_thread.attention_id
                self.text_edit.append("System: 已设置目标ID为" + str(self.video_thread.target_id) + "！\n")
            else:
                self.text_edit.append("System: 请先选择目标!\n")
                return
        if not self.video_thread.enable_track:
            self.video_thread.toggle_track()
            self.text_edit.append("System: 开始追踪!\n")
            self.video_thread.track_timer.start(50)

    def disable_track(self):
        if not self.video_thread.enable:
            self.text_edit.append("System: 请开启摄像头！\n")
            return
        elif self.video_thread.robot is None:
            self.text_edit.append("System: 请先连接机器人!\n")
            return
        elif self.video_thread.target_id == 0:
            self.text_edit.append("System: 请先选择目标!\n")
            return
        if self.video_thread.enable_track:
            self.video_thread.toggle_track()
            self.text_edit.append("System: 停止追踪!\n")
            self.video_thread.track_timer.stop()
            self.robot.servo_move_enable(False)

    def toggle_track(self):
        if not self.video_thread.enable:
            self.text_edit.append("System: 请开启摄像头！\n")
            return
        elif self.video_thread.robot is None:
            self.text_edit.append("System: 请先连接机器人!\n")
            return
        elif self.video_thread.target_id == 0:
            self.text_edit.append("System: 请先选择目标!\n")
            return
        self.video_thread.toggle_track()
        if self.video_thread.enable_track:
            self.text_edit.append("System: 开始追踪!\n")
            self.video_thread.track_timer.start(50)
        else:
            self.text_edit.append("System: 停止追踪!\n")
            self.video_thread.track_timer.stop()
            self.robot.servo_move_enable(False)

    def set_record_config(self, ci=33, fps=30, hd=0, sf=1, vd=0):
        self.video_thread.cap_interval = ci
        self.video_thread.hd = hd
        self.video_thread.sf = sf
        self.video_thread.vd = vd
        date = str(datetime.datetime.now().strftime('%Y-%m-%d'))
        current_time = str(datetime.datetime.now().strftime('%H-%M-%S'))
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.video_thread.video_writer = cv2.VideoWriter("video/" + date + "/" + current_time + ".mp4", fourcc, fps,
                                                         (self.video_thread.frame.shape[1],
                                                          self.video_thread.frame.shape[0]))

    def toggle_record(self, ci=33, fps=30, hd=0, sf=1, vd=0):
        if not self.video_thread.enable:
            self.text_edit.append("System: 请开启摄像头！\n")
            return
        self.video_thread.toggle_record()
        if self.video_thread.enable_record:
            self.text_edit.append("System: 开始录像!\n")
            # 如果video文件夹中没有今天日期的文件夹，则创建
            date = str(datetime.datetime.now().strftime('%Y-%m-%d'))
            if not os.path.exists("video/" + date):
                os.makedirs("video/" + date)
            # 创建视频文件
            self.set_record_config(ci, fps, hd, sf, vd)
            self.video_thread.record_timer.start(ci)
        else:
            self.text_edit.append("System: 停止录像!\n")
            self.video_thread.record_timer.stop()
            self.video_thread.video_writer.release()

    # def record(self):
    #     while self.video_thread.enable_record:
    #         self.video_thread.record()

    def select_id(self):
        target_id = self.id_input_box.value()
        if target_id not in [obj[0] for obj in self.video_thread.obj_info]:
            self.text_edit.append("System: 无效ID！\n")
            return
        # if self.video_thread.enable:
        #     self.toggle_camera()
        self.target_id = target_id
        self.video_thread.target_id = self.target_id
        # self.toggle_camera()
        self.text_edit.append("System: 已设置目标ID为" + str(self.target_id) + "！\n")

    # def ask_id(self):
    #     self.text_edit.append("System: 请选择目标ID！输入 'cancel' 取消！\n")
    #     self.line_edit.setFocus()
    #     self.send_button.clicked.connect(self.choose_id)
    #     self.line_edit.returnPressed.connect(self.choose_id)
    #
    # def choose_id(self):
    #
    #     if self.line_temp == "cancel":
    #         self.text_edit.append("System: 取消选择！\n")
    #         self.send_button.clicked.disconnect(self.choose_id)
    #         self.line_edit.returnPressed.disconnect(self.choose_id)
    #         self.toggle_camera()
    #         return
    #     elif not self.line_temp.isnumeric():
    #         self.text_edit.append("System: 请输入数字ID！重新选择或输入 'cancel' 取消！\n")
    #         self.line_edit.setFocus()
    #         return
    #     elif int(self.line_temp) not in [obj[3] for obj in self.video_thread.obj_info]:
    #         self.text_edit.append("System: ID不存在！重新选择或输入 'cancel' 取消！\n")
    #         self.line_edit.setFocus()
    #         return
    #
    #     self.target_id = int(self.line_temp)
    #     if self.video_thread.enable:  ################################################################?????
    #         self.toggle_camera()
    #     self.video_thread.target_id = self.target_id
    #     self.toggle_camera()
    #     self.text_edit.append("System: 目标ID为" + str(self.video_thread.target_id) + "！\n")
    #     self.send_button.clicked.disconnect(self.choose_id)
    #     self.line_edit.returnPressed.disconnect(self.choose_id)

    def clear_record(self):
        self.text_edit.clear()

    def send_message(self):
        # 从 QLineEdit 控件中读取文本
        text = self.line_edit.text()
        self.update_camera_prompt(text)
        self.line_temp.append(text)
        self.text_edit.append("User：" + text + "\n")
        self.line_edit.clear()
        if self.enable_GPT:
            self.get_gpt_answer_thread.question = text
            self.get_gpt_answer_thread.start()

    def audio2text(self):
        self.audio2text_thread.start()
        self.line_edit.setFocus()

    def stop_threads(self):
        self.video_thread.stop()
        self.video_thread.wait()
        self.wake_thread.stop()
        self.wake_thread.terminate()

    def toggle_gpt(self):
        self.enable_GPT = not self.enable_GPT
        if self.enable_GPT:
            self.GPT_button.setText("关闭GPT")
            self.text_edit.append("System: GPT已开启！\n")
        else:
            self.GPT_button.setText("开启GPT")
            self.text_edit.append("System: GPT已关闭！\n")

    def update_gpt(self, new_gpt):
        self.GPT = new_gpt

    # def toggle_record(self):
    #     self.record_thread.enable_record = not self.record_thread.enable_record
    #     if self.record_thread.enable_record:
    #         self.text_edit.append("System: 录像已开始！\n")
    #         self.record_thread.start()
    #     else:
    #         self.text_edit.append("System: 录像已结束！\n")
    #         self.record_thread.stop()
    #         self.record_thread.wait()

    def toggle_wake(self):
        if not self.wake_thread.isRunning():
            self.wake_thread.start()
            self.wake_button.setText("关闭唤醒模式")
            self.text_edit.append("System: 唤醒模式已打开！\n")
        else:
            self.wake_thread.terminate()
            self.wake_button.setText("打开唤醒模式")
            self.text_edit.append("System: 唤醒模式已关闭！\n")

    def cmd_executor(self, instructions):
        for instruction in instructions:
            if instruction[0] == "Start REC":
                if not self.video_thread.enable:
                    self.text_edit.append("System: 请开启摄像头！\n")
                    tw.text2audio("请开启摄像头！")
                    continue
                if self.video_thread.enable_record:
                    self.text_edit.append("System: 请勿重复开启录像!\n")
                    tw.text2audio("请勿重复开启录像!")
                    continue
                else:
                    self.video_thread.enable_record = True
                    self.text_edit.append("System: 开始录像!\n")
                    tw.text2audio("已为您开启录像!")
            elif instruction[0] == "Stop REC":
                if not self.video_thread.enable:
                    self.text_edit.append("System: 请开启摄像头！\n")
                    tw.text2audio("请开启摄像头！")
                    continue
                if self.video_thread.enable_record:
                    self.video_thread.enable_record = False
                    self.text_edit.append("System: 停止录像!\n")
                    tw.text2audio("已为您停止录像!")
                else:
                    self.text_edit.append("System: 录像未开始!\n")
                    tw.text2audio("录像未开始!")
                    continue
            elif instruction[0] == "id=":
                target_id = int(instruction[1])
                if target_id not in [obj[3] for obj in self.video_thread.obj_info]:
                    self.text_edit.append("System: 无效ID！\n")
                    tw.text2audio("无效ID！")
                    continue
                else:
                    self.target_id = target_id
                    self.video_thread.target_id = self.target_id
                    self.text_edit.append("System: 目标ID为" + str(self.target_id) + "！\n")
                    tw.text2audio("已为您设置目标ID为" + str(self.target_id) + "！")

    def change_mode(self):
        if self.mode_combo.currentIndex() == 2:
            self.text_edit.append("System: 全自动模式已开启！\n")
            self.current_mode.setText("当前模式：全自动模式")
            self.camera_thread.terminate()
            self.enable_GPT = False
            self.enable_camera_thread = False
            self.line_temp = []
            self.auto_thread.start()
        elif self.mode_combo.currentIndex() == 1:
            self.text_edit.append("System: 半自动模式已开启！\n")
            self.current_mode.setText("当前模式：半自动模式")
            self.enable_camera_thread = True
            self.enable_GPT = False
            self.line_temp = []
            self.auto_thread.stop()
        elif self.mode_combo.currentIndex() == 0:
            self.text_edit.append("System: 普通模式已开启！\n")
            self.current_mode.setText("当前模式：普通模式")
            self.toggle_gpt()
            self.camera_thread.terminate()
            self.enable_camera_thread = False
            self.auto_thread.stop()

    def change_track(self):
        if self.track_combo.currentIndex() == 0:
            self.video_thread.mode = "normal"
            self.text_edit.append("System: 自选目标已开启！\n")
            self.current_track_mode.setText("当前追踪模式：自选目标")
        elif self.track_combo.currentIndex() == 1:
            self.video_thread.mode = "random"
            self.text_edit.append("System: 随机模式已开启！\n")
            self.current_track_mode.setText("当前追踪模式：随机模式")
        elif self.track_combo.currentIndex() == 2:
            self.video_thread.mode = "lose_random"
            self.text_edit.append("System: 丢失随机模式已开启！\n")
            self.current_track_mode.setText("当前追踪模式：丢失随机模式")
        elif self.track_combo.currentIndex() == 3:
            self.video_thread.mode = "attention"
            self.text_edit.append("System: 关注模式已开启！\n")
            self.current_track_mode.setText("当前追踪模式：关注模式")
        elif self.track_combo.currentIndex() == 4:
            self.video_thread.mode = "lose_attention"
            self.text_edit.append("System: 丢失关注模式已开启！\n")
            self.current_track_mode.setText("当前追踪模式：丢失关注模式")

    def update_auto_info(self):
        obj_list = self.video_thread.obj_info
        target_info = self.video_thread.target_info
        depth_image = self.video_thread.depth_image

        self.auto_thread.prompt_queue = self.line_temp
        self.line_temp = []

        obj_info_list = []
        # for obj in obj_list:
        #     print(obj[0], obj[1], obj[2], obj[3], obj[4], obj[5].shape)
        for obj in obj_list:
            try:
                obj_dict = {"id": obj[0], "cls": obj[4], "pos": (obj[1], obj[2]),
                            "distance": depth_image[obj[2], obj[1]] if depth_image is not None else np.inf}
                obj_info_list.append(obj_dict)
            except:
                continue
        self.auto_thread.object_list = obj_info_list

        if target_info is None:
            self.auto_thread.target_id = None
            self.auto_thread.target_cls = None
            self.auto_thread.target_gender = None
            self.auto_thread.target_age = None
            self.auto_thread.target_emotion = None
            self.auto_thread.target_pos = None
            self.auto_thread.target_distance = None
        else:
            self.auto_thread.target_id = target_info[0]
            self.auto_thread.target_cls = target_info[4]
            if target_info[4] == 'person':
                face_recognition = \
                    DeepFace.analyze(target_info[5], actions=('gender', 'age', 'emotion'), enforce_detection=False)
                self.auto_thread.target_gender = face_recognition[0]['dominant_gender']
                self.auto_thread.target_age = face_recognition[0]['age']
                self.auto_thread.target_emotion = face_recognition[0]['dominant_emotion']
            else:
                self.auto_thread.target_gender = None
                self.auto_thread.target_age = None
                self.auto_thread.target_emotion = None
            self.auto_thread.target_pos = (target_info[1], target_info[2])
            if depth_image is None:
                self.auto_thread.target_distance = None
            else:
                self.auto_thread.target_distance = depth_image[int(target_info[2]), int(target_info[1])] / 1000

        if self.robot is None:
            self.auto_thread.arm_is_stuck = None
        else:
            self.auto_thread.arm_is_stuck = bool(self.robot.is_on_limit()[1]) or bool(self.robot.is_in_collision()[1])
        self.auto_thread.arm_pos = self.arm_pose_info2.text()

    def toggle_auto_a2t(self):
        self.auto_thread.toggle_a2t()
        if self.auto_thread.a2t_thread.enable_a2t:
            self.text_edit.append("System：已开启语音接收！\n")
        else:
            self.text_edit.append("System：已关闭语音接收！\n")

    def move_emotion(self, emotion):
        if self.robot is None or self.video_thread.enable_track and self.video_thread.lose_count == 0:
            # 如果允许追踪或者机械臂未连接，则不进行情绪移动
            return
        if emotion == "neutral" and (self.video_thread.lose_count > 0 or self.video_thread.target_id == 0):
            return
        self.emotion_thread.emotion = emotion
        self.emotion_thread.start()

    def update_camera_prompt(self, text):
        if self.enable_camera_thread:
            self.camera_thread.update_prompt(text)
            self.camera_thread.start()
        else:
            pass


if __name__ == '__main__':
    # robot = jkrc.RC("10.5.5.100")
    # robot.login()
    # robot.power_on()
    # robot.enable_robot()
    DeepFace.analyze(cv2.imread("1.png"), actions=('gender', 'age', 'emotion'), enforce_detection=False)
    app = QApplication([])
    window = MainWindow()
    window.destroyed.connect(window.stop_threads)
    window.show()
    app.exec_()

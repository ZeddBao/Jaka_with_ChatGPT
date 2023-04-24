# -*- coding: utf-8 -*-

import time
import jkrc

PI = 3.1415926

ABS = 0  # 绝对运动
INCR = 1  # 增量运动
Enable = True
Disable = False

robot = jkrc.RC("10.5.5.100")  # 返回一个机器人对象
robot.login()  # 登录
robot.power_on()  # 上电
robot.enable_robot()
robot.servo_move_enable(Enable)  # 进入位置控制模式
# robot.servo_speed_foresight(20, 1)

print("enable")
time.sleep(1)
for i in range(200):
    robot.servo_p([0, 0, 0.01, 0, 0, 0], move_mode=INCR)
    time.sleep(0.05)
for i in range(200):
    robot.servo_p([0, 0, 0.01, 0, 0, 0], move_mode=INCR)
    time.sleep(0.05)

robot.servo_move_enable(Disable)  # 退出位置控制模式
print("disable")
robot.logout()  # 登出

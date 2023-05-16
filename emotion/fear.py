import jkrc
import random
import time

PI = 3.1415926
ABS = 0
INCR = 1
Enable = True
Disable = False

robot = jkrc.RC("10.5.5.100")
robot.login()


def fear():
    # robot.motion_abort()
    joint_pos = robot.get_joint_position()[1]
    robot.joint_move((-PI * 0.788889, -PI * 0.18888, PI * 0.759, PI * 0.6387, -PI * 0.469099, PI / 4), ABS, False, PI)
    robot.joint_move((PI / 12 + random.uniform(-0.16, 0.16), 0, 0, 0, 0, 0), INCR, False, PI)
    robot.joint_move((-PI / 6 + random.uniform(-0.16, 0.16), 0, 0, 0, 0, 0), INCR, False, PI)
    robot.joint_move((PI / 12 + random.uniform(-0.16, 0.16), 0, 0, 0, 0, 0), INCR, False, PI)
    time.sleep(2)
    robot.joint_move(joint_pos, ABS, False, 1)


if __name__ == '__main__':
    fear()

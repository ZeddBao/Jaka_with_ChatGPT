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


def angry():
    mode = random.randint(1, 3)
    if mode == 1:
        # 打
        # robot.motion_abort()
        joint_pos = robot.get_joint_position()[1]
        robot.joint_move((-PI * 0.7833, PI * 0.6730, PI * 0.1142, PI * 0.1080, -PI * 0.4653, PI * 0.25), ABS, False, PI)
        robot.joint_move((0, PI / 4, 0, 0, 0, 0), INCR, False, PI)
        robot.joint_move((0, -PI / 4, 0, 0, 0, 0), INCR, False, PI)
        robot.joint_move(joint_pos, ABS, False, 1)

    if mode == 2:
        # 扭头
        robot.motion_abort()
        joint_pos = robot.get_joint_position()[1]
        robot.joint_move((0, 0, 0, -PI / 12, PI * 2 / 3, 0), INCR, False, PI)
        time.sleep(2)
        robot.joint_move(joint_pos, ABS, False, 1)


if __name__ == '__main__':
    angry()

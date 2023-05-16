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


def sad():
    # robot.motion_abort()
    joint_pos = robot.get_joint_position()[1]
    print(joint_pos)
    robot.joint_move((random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16), PI * 1 / 6,
                      random.uniform(-0.16, 0.16), 0), INCR, False, PI)
    robot.joint_move((random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16),
                      random.uniform(-0.16, 0.16), -PI * 1 / 4, 0), INCR, False, PI)
    robot.joint_move((random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16),
                      random.uniform(-0.16, 0.16), PI * 1 / 2, 0), INCR, False, PI)
    robot.joint_move((random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16),
                      random.uniform(-0.16, 0.16), -PI * 1 / 4, 0), INCR, False, PI)
    time.sleep(2)
    robot.joint_move(joint_pos, ABS, False, 1)


if __name__ == '__main__':
    sad()

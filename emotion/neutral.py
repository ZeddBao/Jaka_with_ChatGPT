import jkrc
import random
import numpy as np

PI = 3.1415926
ABS = 0
INCR = 1
Enable = True
Disable = False

robot = jkrc.RC("10.5.5.100")
robot.login()


def neutral():
    # robot.motion_abort()
    joint_pos = robot.get_joint_position()[1]
    joint_pos_new = joint_pos.copy()
    joint_pos_new[4] = -PI / 2
    if -PI * 3 / 2 < joint_pos[4] < PI / 2:
        robot.joint_move((0, 0, 0, 0, np.random.normal(loc=0.0, scale=0.5), 0), INCR, False, PI)
        robot.joint_move((0, 0, 0, 0, np.random.normal(loc=0.0, scale=0.5), 0), INCR, False, PI)
        robot.joint_move((0, 0, 0, 0, np.random.normal(loc=0.0, scale=0.5), 0), INCR, False, PI)
        robot.joint_move((0, 0, 0, 0, np.random.normal(loc=0.0, scale=0.5), 0), INCR, False, PI)
    else:
        robot.joint_move(joint_pos_new, ABS, False, 1)
    # if joint_pos_new[4] > 2:
    #     robot.joint_move(joint_pos, ABS, False, 1)


if __name__ == '__main__':
    neutral()

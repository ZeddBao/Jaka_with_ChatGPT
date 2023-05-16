import jkrc
import random
import time
import numpy as np

PI = 3.1415926
ABS = 0
INCR = 1
Enable = True
Disable = False
robot = jkrc.RC("10.5.5.100")


def neutral():
    # robot.motion_abort()
    joint_pos = robot.get_joint_position()[1]
    joint_pos_new = joint_pos.copy()
    joint_pos_new[4] = -PI / 2
    if -PI * 3 / 2 < joint_pos[4] < PI / 2:
        robot.joint_move((0, 0, 0, 0, np.random.normal(loc=0.0, scale=0.5), 0), INCR, False, PI)
        time.sleep(2)
        robot.joint_move((0, 0, 0, 0, np.random.normal(loc=0.0, scale=0.5), 0), INCR, False, PI)
        time.sleep(2)
        robot.joint_move((0, 0, 0, 0, np.random.normal(loc=0.0, scale=0.5), 0), INCR, False, PI)
        time.sleep(2)
        robot.joint_move((0, 0, 0, 0, np.random.normal(loc=0.0, scale=0.5), 0), INCR, False, PI)
    else:
        robot.joint_move(joint_pos_new, ABS, False, 1)
    # if joint_pos_new[4] > 2:
    #     robot.joint_move(joint_pos, ABS, False, 1)


def happy():
    mode = random.randint(1, 6)
    if mode == 1:
        # robot.motion_abort()
        joint_pos = robot.get_joint_position()[1]
        print(joint_pos)
        robot.joint_move((PI / 8, PI / 8, -PI / 4, PI / 8 + random.uniform(random.uniform(-0.16, 0.16), 0.16),
                          random.uniform(-0.16, 0.16), 0), INCR, False, PI)
        robot.joint_move((-PI / 8, -PI / 8, PI / 4, -PI / 8, random.uniform(-0.16, 0.16), 0), INCR, False, PI)
        robot.joint_move((-PI / 8, PI / 8, -PI / 4 + random.uniform(random.uniform(-0.16, 0.16), 0.16), PI / 8,
                          random.uniform(-0.16, 0.16), 0), INCR, False, PI)
        robot.joint_move((PI / 8 + random.uniform(random.uniform(-0.16, 0.16), 0.16), -PI / 8, PI / 4, -PI / 8,
                          random.uniform(-0.16, 0.16), 0), INCR, False, PI)
        robot.joint_move(joint_pos, ABS, False, 1)

    elif mode == 2:
        # robot.motion_abort()
        joint_pos = robot.get_joint_position()[1]
        robot.joint_move((random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16), PI / 8,
                          random.uniform(-0.16, 0.16), 0), INCR, False, PI)
        robot.joint_move(
            (random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16), -PI / 5,
             random.uniform(-0.16, 0.16), 0), INCR, False, PI)
        robot.joint_move((random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16),
                          PI / 6 + random.uniform(random.uniform(-0.16, 0.16), 0.16), random.uniform(-0.16, 0.16), 0),
                         INCR,
                         False, PI)
        robot.joint_move((random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16),
                          -PI / 5 + random.uniform(random.uniform(-0.16, 0.16), 0.16), random.uniform(-0.16, 0.16), 0),
                         INCR, False, PI)
        robot.joint_move(joint_pos, ABS, False, 1)
    elif mode == 3:
        # robot.motion_abort()
        joint_pos = robot.get_joint_position()[1]
        robot.joint_move((PI / 8, random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16),
                          PI / 8 + random.uniform(random.uniform(-0.16, 0.16), 0.16), random.uniform(-0.16, 0.16), 0),
                         INCR,
                         False, PI)
        robot.joint_move(
            (
                -PI / 3, random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16), -PI / 6, random.uniform(-0.16, 0.16),
                0),
            INCR, False, PI)
        robot.joint_move((PI / 8, random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16), PI / 8, PI / 8, 0), INCR,
                         False,
                         PI)
        robot.joint_move((-PI / 4, random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16), -PI / 6, -PI / 4, 0), INCR,
                         False, PI)
        robot.joint_move(joint_pos, ABS, False, 1)

    elif mode == 4:
        # 前仰后合 robot.motion_abort() joint_pos = robot.get_joint_position()[1] robot.joint_move((random.uniform(-0.16,
        # 0.16), PI / 8 + random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16),
        # random.uniform(-0.16, 0.16), 0), INCR, False, PI) robot.joint_move((random.uniform(-0.16, 0.16),
        # random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16), PI/8 + random.uniform(-0.16, 0.16),
        # random.uniform( -0.16, 0.16), 0), INCR, False, PI) robot.joint_move((random.uniform(-0.16, 0.16),
        # random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16), -PI / 8 + random.uniform(-0.16, 0.16),
        # random.uniform(-0.16, 0.16), 0), INCR, False, PI) robot.joint_move((random.uniform(-0.16, 0.16),
        # random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16), PI / 8 + random.uniform(-0.16, 0.16),
        # random.uniform(-0.16, 0.16), 0), INCR, False, PI) robot.joint_move((random.uniform(-0.16, 0.16),
        # random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16), -PI / 8 + random.uniform(-0.16, 0.16),
        # random.uniform(-0.16, 0.16), 0), INCR, False, PI) robot.joint_move(( random.uniform(-0.16, 0.16),
        # random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16), PI / 8 + random.uniform( -0.16, 0.16),
        # random.uniform(-0.16, 0.16), 0), INCR, False, PI) robot.joint_move((random.uniform(-0.16, 0.16),
        # random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16), -PI / 8 + random.uniform(-0.16, 0.16),
        # random.uniform(-0.16, 0.16), 0), INCR, False, PI) robot.joint_move(joint_pos, ABS, False, 1)
        joint_pos = robot.get_joint_position()[1]
        robot.joint_move(
            (random.uniform(-0.16, 0.16), PI / 8 + random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16),
             random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16), 0), INCR, False, PI)
        robot.joint_move((random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16),
                          PI / 8 + random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16), 0), INCR, False, PI)
        robot.joint_move((random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16),
                          -PI / 8 + random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16), 0), INCR, False, PI)
        robot.joint_move((random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16),
                          PI / 8 + random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16), 0), INCR, False, PI)
        robot.joint_move((random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16),
                          -PI / 8 + random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16), 0), INCR, False, PI)
        robot.joint_move((random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16),
                          PI / 8 + random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16), 0), INCR, False, PI)
        robot.joint_move((random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16),
                          -PI / 8 + random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16), 0), INCR, False, PI)
        robot.joint_move(joint_pos, ABS, False, 1)

    elif mode == 5:
        # robot.motion_abort() joint_pos = robot.get_joint_position()[1] robot.joint_move((random.uniform(-0.16, 0.16),
        # random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16), random.uniform(-0.16,
        # 0.16), PI / 6 + random.uniform(random.uniform(-0.16, 0.16), 0.16)), INCR, False, PI) robot.joint_move((
        # random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16), random.uniform(-0.16,
        # 0.16), random.uniform(-0.16, 0.16), -PI / 3 + random.uniform(random.uniform(-0.16, 0.16), 0.16)), INCR, False,
        # PI) robot.joint_move(joint_pos, ABS, False, 1) robot.motion_abort()
        joint_pos = robot.get_joint_position()[1]
        robot.joint_move((random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16),
                          random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16),
                          PI / 6 + random.uniform(random.uniform(-0.16, 0.16), 0.16)), INCR, False, PI)
        robot.joint_move((random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16),
                          random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16),
                          -PI / 3 + random.uniform(random.uniform(-0.16, 0.16), 0.16)), INCR, False, PI)
        robot.joint_move(joint_pos, ABS, False, 1)


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


def fear():
    # robot.motion_abort()
    joint_pos = robot.get_joint_position()[1]
    robot.joint_move((-PI * 0.788889, -PI * 0.18888, PI * 0.759, PI * 0.6387, -PI * 0.469099, PI / 4), ABS, False, PI)
    robot.joint_move((PI / 12 + random.uniform(-0.16, 0.16), 0, 0, 0, 0, 0), INCR, False, PI)
    robot.joint_move((-PI / 6 + random.uniform(-0.16, 0.16), 0, 0, 0, 0, 0), INCR, False, PI)
    robot.joint_move((PI / 12 + random.uniform(-0.16, 0.16), 0, 0, 0, 0, 0), INCR, False, PI)
    time.sleep(2)
    robot.joint_move(joint_pos, ABS, False, 1)


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

import jkrc
import random

PI = 3.1415926
ABS = 0
INCR = 1
Enable = True
Disable = False

robot = jkrc.RC("10.5.5.100")
robot.login()


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
            -PI / 3, random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16), -PI / 6, random.uniform(-0.16, 0.16), 0),
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
        # random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16), PI/8 + random.uniform(-0.16, 0.16), random.uniform(
        # -0.16, 0.16), 0), INCR, False, PI) robot.joint_move((random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16),
        # random.uniform(-0.16, 0.16), -PI / 8 + random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16), 0), INCR,
        # False, PI) robot.joint_move((random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16), random.uniform(-0.16,
        # 0.16), PI / 8 + random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16), 0), INCR, False,
        # PI) robot.joint_move((random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16),
        # -PI / 8 + random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16), 0), INCR, False, PI) robot.joint_move((
        # random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16), PI / 8 + random.uniform(
        # -0.16, 0.16), random.uniform(-0.16, 0.16), 0), INCR, False, PI) robot.joint_move((random.uniform(-0.16, 0.16),
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


if __name__ == "__main__":
    pass

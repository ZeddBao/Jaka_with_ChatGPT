import jkrc
import time

PI = 3.1415926
ABS = 0
INCR = 1
Enable = True
Disable = False

robot = jkrc.RC("10.5.5.100")
robot.login()
# robot.power_on()
# robot.enable_robot()

robot_joint = robot.get_joint_position()
print(robot_joint)
print(robot_joint[1])

for i in range(5):

    robot_joint[1][4] = robot_joint[1][4] + PI / 3
    robot.joint_move(robot_joint[1], ABS, True, 1)
    time.sleep(1)

robot.joint_move((0, PI/2, 0, 0, 0, 0), ABS, True, 1)

time.sleep(10)
robot.logout()

# robot.servo_move_enable(Enable)
# robot_pos = robot.get_tcp_position()
# print(robot_pos[1])
# robot_pos[1][2] = robot_pos[1][2] - 50
# robot.servo_p(cartesian_pose = robot_pos[1], move_mode = INCR)
# robot.servo_move_enable(Disable)

# time.sleep(1)
# robot.logout()

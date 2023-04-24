import jkrc

PI = 3.1415926
ABS = 0
INCR = 1
Enable = True
Disable = False

robot = jkrc.RC("10.5.5.100")
robot.login()
robot.power_on()
robot.enable_robot()
x = -PI / 5
robot.joint_move((-PI*3/4, PI / 3, PI / 3, PI*1 / 3, -PI/2, PI / 4), ABS, False, 1)  # default
robot.joint_move((0, x, -2 * x, x, 0, 0), INCR, False, 1)  # default

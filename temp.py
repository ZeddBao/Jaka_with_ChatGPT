# -*- coding: GBK -*-
import jkrc
import time
import math
PI = 3.1415926
pi = 3.1415926
Pi = 3.1415926
ABS = 0
INCR = 1
Enable = True
Disable = False
robot = jkrc.RC("10.5.5.100")
robot.login()

robot.joint_move((0, 0, 0, 0, 0, math.pi/6), 1, False, 1)

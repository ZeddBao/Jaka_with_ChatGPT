# 导入必要的包
from AIDetector_pytorch import Detector
import imutils
import cv2
import jkrc
import time


def ask_ids(detector):

    # 设置窗口的名称以显示视频输入
    name = 'ask_ids'

    # 打开默认摄像头（0）
    cap = cv2.VideoCapture(2)

    obj_info = []
    result = []
    while True:
        # 从摄像头读取一帧
        _, im = cap.read()

        # 如果没有更多的帧，则跳出循环
        if im is None:
            break

        # 使用检测器处理帧
        result = detector.feedCap(im)
        obj_info = result['obj_info']

        result = result['frame']

        # 在窗口中显示处理后的帧
        cv2.imshow(name, result)

        # 如果按“q“，则跳出循环
        if cv2.waitKey(1) == ord("q"):
            break

    # 释放摄像头和视频写入对象，并关闭窗口
    cap.release()
    if obj_info is not None:
        for obj in obj_info:
            print("坐标：(" + str(obj[0]) + "," + str(obj[1]) + ")    面积：" + str(obj[2]) + "    id：" + str(obj[3]))
        cv2.imshow(name, result)
        t_id = int(input("选择你要的需要追踪的id："))
        cv2.destroyAllWindows()
        return t_id
    else:
        cv2.destroyAllWindows()
        print("未检测到人！")
        return -1


# 定义主函数
def main_detect(detector, t_id, x_kp=0.1, x_ki=0, x_kd=0, y_kp=0.1, y_ki=0, y_kd=0):
    # 设置窗口的名称以显示视频输入
    name = 'main_detect'

    # 初始化检测器
    # det = Detector()

    # 打开默认摄像头（0），并获取它的帧率
    cap = cv2.VideoCapture(2)
    # fps = int(cap.get(5))
    # print('fps:', fps)
    # 计算帧之间的延迟以实现所需的帧率
    # t = int(1000 / fps)

    # 初始化视频写入对象
    # videoWriter = None

    ex = 0
    ey = 0
    dx = 0
    dy = 0
    ix = 0
    iy = 0
    cx = 0
    cy = 0
    # 循环处理来自摄像头的帧
    while True:
        time.sleep(0.04)

        # 从摄像头读取一帧
        _, im = cap.read()

        # 如果没有更多的帧，则跳出循环
        if im is None:
            break

        if cx == 0:
            cx = im.shape[1] / 2
            cy = 2*im.shape[0] / 3

        # 使用检测器处理帧
        result = detector.feedCap(im)
        obj_info = result['obj_info']
        flag = 0
        for obj in obj_info:
            if obj[3] == t_id:
                flag = 1
                print("坐标：(", obj[0], ",", obj[1], ")    面积：", obj[2], "    id：", obj[3])
                print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                x_output = x_kp * (obj[0] - cx) + x_kd * (obj[0] - cx - ex) + x_ki * (obj[0] - cx + ix)
                if x_output > 0.005:
                    x_output = 0.005
                elif x_output < -0.005:
                    x_output = -0.005
                y_output = y_kp * (obj[1] - cy) + y_kd * (obj[1] - cy - ey) + y_ki * (obj[1] - cy + iy)
                if y_output > 0.001:
                    y_output = 0.001
                elif y_output < -0.001:
                    y_output = -0.001
                ex = obj[0] - cx
                ey = obj[1] - cy
                print("x误差：", ex, "    y误差：", ey, "    x输出：", x_output, "    y输出：", y_output)
                print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                ix += ex
                iy += ey
                robot.servo_j(joint_pos=[0, -y_output, 2*y_output, -y_output, -x_output, 0], move_mode=1)
                # robot.servo_p(cartesian_pos=[0, 0, y_output, 0, 0, 0], move_mode=1)
                break
        if flag == 0:
            print("失去目标")
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

        result = result['frame']
        # result = imutils.resize(result, height=500)

        # 使用正确的编解码器、帧率和尺寸初始化视频写入对象
        # if videoWriter is None:
        #     fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')  # opencv3.0
        #     videoWriter = cv2.VideoWriter('result.mp4', fourcc, fps, (result.shape[1], result.shape[0]))

        # 将处理后的帧写入输出视频文件
        # videoWriter.write(result)

        # 在窗口中显示处理后的帧
        cv2.imshow(name, result)

        # 等待帧之间的指定时间
        # cv2.waitKey(t)

        # 如果按“q“，则跳出循环
        if cv2.waitKey(1) == ord("q"):
            break

    # 释放摄像头和视频写入对象，并关闭窗口
    cap.release()
    # videoWriter.release()
    cv2.destroyAllWindows()


# 如果这个文件作为主程序运行，则调用主函数
if __name__ == '__main__':
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

    det = Detector()
    target_id = ask_ids(det)
    main_detect(det, target_id)

# 导入必要的包
from AIDetector_pytorch import Detector
import imutils
import cv2
import jkrc
import numpy as np

camera_shape = []


def ask_ids(detector):
    # 设置窗口的名称以显示视频输入
    name = 'ask_ids'

    # 打开默认摄像头（0）
    cap = cv2.VideoCapture(0)

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
def main_detect(detector, t_id):
    global camera_shape
    # 设置窗口的名称以显示视频输入
    name = 'main_detect'

    # 初始化检测器
    # det = Detector()

    # 打开默认摄像头（0），并获取它的帧率
    cap = cv2.VideoCapture(0)
    # fps = int(cap.get(5))
    # print('fps:', fps)
    # 计算帧之间的延迟以实现所需的帧率
    # t = int(1000 / fps)

    # 初始化视频写入对象
    # videoWriter = None

    # 循环处理来自摄像头的帧
    while True:

        # 从摄像头读取一帧
        _, im = cap.read()

        # 如果没有更多的帧，则跳出循环
        if im is None:
            break

        # 使用检测器处理帧
        result = detector.feedCap(im)
        obj_info = result['obj_info']
        flag = 0
        for obj in obj_info:
            if obj[3] == t_id:
                flag = 1
                print("坐标：(" + str(obj[0]) + "," + str(obj[1]) + ")    面积：" + str(obj[2]) + "    id：" + str(obj[3]))
                print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                break
        if flag == 0:
            print("失去目标")
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

        result = result['frame']
        camera_shape = np.array(result).shape
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
    det = Detector()
    target_id = ask_ids(det)
    main_detect(det, target_id)
    print(camera_shape)

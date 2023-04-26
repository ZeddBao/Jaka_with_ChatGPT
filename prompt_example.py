import openai
import os
import re


# 用正则表达式把一段文字中``` ```或''' '''中的内容提取出来
def get_code(text):
    pattern = re.compile(r"```python(.*?)```", re.S)
    match = pattern.findall(text)
    if match:
        return match[0]
    pattern = re.compile(r"```(.*?)```", re.S)
    match = pattern.findall(text)
    if match:
        return match[0]
    return ""


# 把字符串写入一个python文件
def write_code(code):
    with open("example.txt", "r") as f:
        example = f.read()
    code = example.replace("# replace the text", code)
    with open("temp.py", "w") as f:
        f.write(code)


def prompt2motion():
    openai.api_key = "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"
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "如果是调整追踪参数的指令，回答请以如下的形式输出：\n"
                                    "例如需要参考点向下一点，输出字符串'@@y--@@，向上一点则输出'@@y++@@，向左一点则输出'@@x--@@，向右一点则输出'@@x++@@，\n"
                                    "参考点向下30个像素点则输出'@@y-=30@@，向右30个像素点则输出'@@x+=30@@，\n"
                                    "例如需要改变追踪id为1，输出字符串'@@id=1@@'\n"
                                    "如果是运动控制类的指令，回答请直接输出在程序代码块里，在代码块之外回答'动作执行完毕！'。不要导入任何库。不要导入任何库。不要导入任何库。"
        # {"role": "user", "content": "现在有一个控制机械臂运动的python函数：robot.joint_move(joint_pos, move_mode, is_block, speed)。\n"
        #                             "joint_pos: 类型为一个6元素的元组，元组中的每个元素代表机械臂对应关节旋转角度，正数为顺时针，负数为逆时针，单位：rad。\n"
        #                             "move_mode: 类型为int变量，默认为 1，1 代表相对运动。\n "
        #                             "is_block: 类型为bool变量，默认为 False，设置接口是否为阻塞接口，TRUE 为阻塞接口 FALSE 为非阻塞接口，"
        #                             "阻塞表示机器人运动完成才会有返回值，非阻塞表示接口调用完成立刻就有返回值。\n"
        #                             "speed: 类型为浮点型变量，默认为 1，机器人关节运动速度，单位：rad/s。\n"
        #                             "你只需要按照后面例子的格式进行回答。例子: robot.joint_move((0, PI/2, 0, 0, 0, 0), 1, False, 1)。\n"
        #                             "记住：只要输出程序代码块，然后在代码块之外输出语句'动作执行完毕！'。只要输出程序代码块，然后在代码块之外输出语句'动作执行完毕！'。"},
                                    "现在有一个控制机械臂每个关节运动的python函数：robot.joint_move(joint_pos, 1, False, 1)。\n"
                                    "joint_pos: 类型为一个6元素的元组，元组中的每个元素代表机械臂对应关节旋转角度，正数为顺时针，负数为逆时针，单位：rad。\n"
                                    "你只需要按照后面例子的格式进行回答。例子: robot.joint_move((0, PI/2, 0, 0, 0, 0), 1, False, 1)。\n"
                                    "记住：一定要输出程序代码块，然后在代码块之外输出语句'动作执行完毕！'。只要输出程序代码块，然后在代码块之外输出语句'动作执行完毕！'。"
                                    "还有一个控制机械臂运动的python函数：robot.linear_move(end_pos, 1, False, 10)。\n"
                                    "end_pos: 类型为一个6元素的元组(x, y, z, rx, ry, rz)，"
                                    "元组中的每个元素代表向该方向上移动的距离，x向左正向右负，y向前正向后负，z向上正向下负，单位：mm，注意单位的换算。\n"
                                    "你只需要按照后面例子的格式进行回答。例子: robot.linear_move((20, 100, -50, 0, 0, 0), 1, False, 10)。\n"
                                    "如果要求方向是斜向方向，需要用勾股定理计算，例如要求向左下移动20 mm，应输出："
                                    "robot.linear_move((20/math.sqrt(2), 0, -20/math.sqrt(2), 0, 0, 0), 1, False, 10)\n"
                                    "记住：一定要输出程序代码块里，然后在代码块之外输出语句'动作执行完毕！'。只要输出程序代码块，然后在代码块之外输出语句'动作执行完毕！'。"},
        {"role": "assistant", "content": "好的，那么您需要我做什么样的代码呢？"}
    ]

    try:
        while True:
            messages.append({"role": "user", "content": input("User: ")})
            # 样例：让机械臂第一个关节顺时针旋转pi。
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages
            )

            ans = completion.choices[0].message
            print(ans.role + ": " + ans.content + '\n')
            code = get_code(ans.content)
            if code == "":
                continue
            write_code(code)
            flag = os.system("python temp.py")
            if not flag:
                err = "出错啦！请重试！"
            ans.content = ans.content.replace("\n", "")
            ans.content = re.sub(r"(.*)```(.*)```", "", ans.content)
            print(ans.role + ": " + ans.content + '\n')
            messages.append(ans)

    except KeyboardInterrupt:
        pass
    print('Range over!')


if __name__ == '__main__':
    prompt2motion()

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
        {"role": "user", "content": "接下来的回答请直接输出程序代码块。不要导入任何库。不要导入任何库。不要导入任何库。"},
        {"role": "assistant", "content": "好的，我会尽力遵守您的要求。有什么可以帮您的吗？"},
        {"role": "user", "content": "现在有一个控制机械臂运动的python函数：robot.joint_move(joint_pos, move_mode, is_block, speed)。\n"
                                    "joint_pos: 类型为一个6元素的元组，元组中的每个元素代表机械臂对应关节旋转角度，正数为顺时针，负数为逆时针，单位：rad。\n"
                                    "move_mode: 类型为int变量，1 代表相对运动。\n "
                                    "is_block: 类型为bool变量,设置接口是否为阻塞接口，TRUE 为阻塞接口 FALSE "
                                    "为非阻塞接口，阻塞表示机器人运动完成才会有返回值，非阻塞表示接口调用完成立刻就有返回值。\n"
                                    "speed: 类型为浮点型变量，机器人关节运动速度，单位：rad/s。\n"
                                    "同时还有另一个控制机械臂运动的python函数：robot.linear_move(end_pos, move_mode, is_block, speed)。\n"
                                    "end_pos: 机器人末端运动目标位置,类型为一个六元素的元组，依次对应坐标系参数x,y,z,rx,ry,rz。\n"
                                    "move_mode: 0 代表绝对运动，1 代表相对运动。\n "
                                    "is_block: 设置接口是否为阻塞接口，TRUE 为阻塞接口 FALSE 为非阻塞接口 "
                                    "为非阻塞接口，阻塞表示机器人运动完成才会有返回值，非阻塞表示接口调用完成立刻就有返回值。\n"
                                    "speed: 机器人直线运动速度，单位：mm/s。\n"
                                    "你可以按照后面例子的格式进行回答。例子: robot.joint_move((0, PI/2, 0, 0, 0, 0), 1, True, 1)\n "
                                    "你可以按照后面例子的格式进行回答。例子: robot.linear_move([1,1,1,0,0,0], 1, TRUE, 1)\n"
                                    "但你需要根据指令判断使用哪一函数生成代码。 "},
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
            messages.append(ans)
            print(ans.role + ": " + ans.content + '\n')
            code = get_code(ans.content)
            if code == "":
                continue
            write_code(code)
            flag = os.system("python temp.py")
            if not flag:
                err = "出错啦！请重试！"

    except KeyboardInterrupt:
        pass
    print('Range over!')


if __name__ == '__main__':
    prompt2motion()

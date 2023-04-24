import os
flag = os.system("python temp.py")
if flag != 0:
    print("动作执行失败！")
else:
    print("动作执行成功！")
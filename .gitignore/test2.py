import os
import threading

t = threading.Thread(target=os.system, args=("python test.py",))
# 运行test.py
print("hello 2")
t.start()
print("hello 2")

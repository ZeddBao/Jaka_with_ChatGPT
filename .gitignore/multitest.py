import threading
import time

def tar(text='2'):
    for i in range(100):
        print(text)


T2 = threading.Thread(target=tar, args="2")
T3 = threading.Thread(target=tar, args="3")
T2.start()
T3.start()
T2.join()

for i in range(100):
    print("1")

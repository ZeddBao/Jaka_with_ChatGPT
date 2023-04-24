import signal
import subprocess


class TimeoutException(Exception):
    pass


def run_with_timeout(cmd, timeout):
    def signal_handler(signum, frame):
        raise TimeoutException("Timed out!")

    # 设置信号处理函数
    signal.signal(signal.SIGTERM, signal_handler)

    # 设置超时时间


    try:
        # 执行命令
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
    except TimeoutException as e:
        print("Command timed out!")
        return None
    except subprocess.CalledProcessError as e:
        print("Error occurred:", e)
        return None
    finally:
        # 取消信号设置
        signal.alarm(0)

    return output


# 超时时间为5秒
timeout = 5

# 要执行的命令
cmd = "sleep 10"

# 在子进程中执行命令，并设置超时时间
output = run_with_timeout(cmd, timeout)

if output is not None:
    print("Command output:", output.decode())

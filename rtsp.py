# opencv_demo.py
# OpenCV-Python timeout for opening a non-existent RTSP video stream
import threading
import time

import cv2

TIME_LIMITED: int = 5


class MyThread(threading.Thread):
    def __init__(self, target, args=()):
        super(MyThread, self).__init__()
        self.func = target
        self.args = args

    def run(self):
        self.result = self.func(*self.args)

    def get_result(self):
        try:
            return self.result
        except Exception:
            return None


# Decorator to limit the actual request time or function execution time
def limit_decor(limit_time):
    """
    :param limit_time: Set the maximum allowable execution time, unit: second
    :return: Untimed returns the value of the decorated function; timed out returns None
    """

    def functions(func):
        def run(*params):
            thre_func = MyThread(target=func, args=params)
            # The thread method terminates when the main thread terminates (exceeds its length)
            thre_func.setDaemon(True)
            thre_func.start()
            # Count the number of segmental slumbers
            sleep_num = int(limit_time // 1)
            sleep_nums = round(limit_time % 1, 1)
            # Sleep briefly several times and try to get the return value
            for i in range(sleep_num):
                time.sleep(1)
                infor = thre_func.get_result()
                if infor:
                    return infor
            time.sleep(sleep_nums)
            # Final return value (whether or not the thread has terminated)
            if thre_func.get_result():
                return thre_func.get_result()
            else:
                return (False, None)  # Timeout returns can be customized

        return run

    return functions


@limit_decor(TIME_LIMITED)
def video_capture_open(rtsp):
    capture = cv2.VideoCapture(rtsp)
    return (True, capture)


def frame_get(rtsp):
    try:
        cap_status, cap = video_capture_open(rtsp)
        return cap_status
    except Exception as err:
        print(err)
        pass


def isOpen(rtsp) -> bool:
    return frame_get(rtsp)


if __name__ == "__main__":
    open = isOpen('rtsp://admin:calming123@192.168.3.110:554/h264Preview_01_sub')
    if not open:
        print('rtsp不可读')
    else:
        print('rtsp可读')

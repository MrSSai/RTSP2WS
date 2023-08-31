import base64
import configparser
import gc
import os
import threading
import time

import schedule
import cv2
from websocket_server import WebsocketServer
from rtsp import isOpen

# 读取 config.ini 文件
config = configparser.ConfigParser()
config.read('config.ini')
# 获取 rtsp_url
rtsp_url = config.get('client', 'rtsp_url')

top = 30
stack = []
read_able = False

client_domain = dict()

lock = threading.Lock()


# 向共享缓冲栈中写入数据:
def write(stack, cam, top: int) -> None:
    """
    :param cam: 摄像头参数
    :param stack: list对象
    :param top: 缓冲栈容量
    :return: None
    """
    print('Process to write: %s' % os.getpid())
    global read_able
    while True:
        if read_able:
            print('流可读，开始读取')
            # videocapture 会一直尝试读取，所以并不是流断开后立即就知道read_able的状态。只有下次check_rtsp_stream执行时，才知道read_able的状态为False
            cap = cv2.VideoCapture(cam)
            while read_able:
                try:
                    _, img = cap.read()
                    if _:
                        stack.append(img)
                        # 每到一定容量清空一次缓冲栈
                        # 利用gc库，手动清理内存垃圾，防止内存溢出
                        if len(stack) >= top:
                            del stack[:]
                            gc.collect()
                except Exception as e:
                    print("Error:", e)
                    read_able = False
        else:
            time.sleep(1)
            print('流断了')


def start_read():
    print('启动监听线程')
    wat_th = threading.Thread(target=watch_thread)
    wat_th.start()

    print('启动抓流线程')
    thread_pro = threading.Thread(target=write,
                                  args=(stack, rtsp_url, top,))
    thread_pro.start()

    start_send()


def start_send():
    print('启动发送消息')
    thread_send = threading.Thread(target=get_frame)
    thread_send.start()


def send_frame(frame, server, client):
    # 将图像转换为 base64 编码的字符串
    retval, buffer = cv2.imencode('.jpg', frame)
    encoded_image = base64.b64encode(buffer.tobytes()).decode('utf-8')
    try:
        server.send_message(client, encoded_image)
    except BaseException:
        print(f'客户端[{client["id"]}]与server断开连接')
        del stack[:]


def get_frame():
    print('使用了get_frame')
    clients = client_domain
    while True:
        if len(stack) != 0:
            # 开始图片消耗
            if len(stack) != 100 and len(stack) != 0:
                value = stack.pop()
            else:
                pass
            if len(stack) >= top:
                del stack[:]
                gc.collect()
            with lock:
                for cl in list(client_domain.keys()):
                    send_frame(value, server, clients[cl])


def check_rtsp_stream():
    global read_able
    try:
        if isOpen(rtsp_url):
            print("RTSP stream is readable.")
            read_able = True
        else:
            read_able = False
    except Exception as e:
        print("Error:", e)
        read_able = False


def watch_thread():
    check_rtsp_stream()
    schedule.every(10).seconds.do(check_rtsp_stream)
    while True:
        schedule.run_pending()
        time.sleep(1)


# Called for every client connecting (after handshake)
def new_client(client, server):
    print("New client connected and was given id %d" % client['id'])
    c_id = client['id']
    client_domain[c_id] = client


# Called for every client disconnecting
def client_left(client, server):
    print("Client(%d) disconnected" % client['id'])
    with lock:
        client_domain.pop(client['id'], None)


# Called when a client sends a message
def message_received(client, server, message):
    if len(message) > 200:
        message = message[:200] + '..'
    print("Client(%d) said: %s" % (client['id'], message))


if __name__ == '__main__':
    start_read()
    PORT = 9001
    server = WebsocketServer(host='0.0.0.0', port=PORT)
    server.set_fn_new_client(new_client)
    server.set_fn_client_left(client_left)
    server.set_fn_message_received(message_received)
    server.run_forever()

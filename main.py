import base64
import configparser
import gc
import os
import threading
import time

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
RUN = False

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
    cap = cv2.VideoCapture(cam)
    # 检查是否成功打开 RTSP 流
    if cap.isOpened():
        print("RTSP 流可读")
    else:
        print("RTSP 流不可读")
    while True:
        _, img = cap.read()
        if _:
            stack.append(img)
            # 每到一定容量清空一次缓冲栈
            # 利用gc库，手动清理内存垃圾，防止内存溢出
            if len(stack) >= top:
                del stack[:]
                gc.collect()


def start_read():
    print('启动抓流线程')
    # 判断rtsp是否可读
    if not isOpen(rtsp_url):
        print('rtsp流不可读')
        return
    # thread_pro = threading.Thread(target=write,
    #                               args=(stack, rtsp_url, top,))
    if not thread_pro.is_alive():
       thread_pro.start()
    start_send()

def start_send():
    print('启动发送消息')
    # thread_send = threading.Thread(target=get_frame)
    if not thread_send.is_alive():
        thread_send.start()
    #thread_send.start()



def check_rtsp_availability():
    cap = cv2.VideoCapture(rtsp_url)
    if not cap.isOpened():
        print("RTSP stream is not currently readable.")

    else:
        start_read()

    cap.release()

def periodic_check():
    while True:
        check_rtsp_availability()
        time.sleep(3)



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
    thread_pro = threading.Thread(target=write,
                                  args=(stack, rtsp_url, top,))
    thread_send = threading.Thread(target=get_frame)

    check_thread = threading.Thread(target=periodic_check)
    check_thread.daemon = True  # 设置为守护线程，程序退出时自动结束线程
    check_thread.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Program terminated.")
    #start_read()
    PORT = 9001
    server = WebsocketServer(host='0.0.0.0', port=PORT)
    server.set_fn_new_client(new_client)
    server.set_fn_client_left(client_left)
    server.set_fn_message_received(message_received)
    server.run_forever()

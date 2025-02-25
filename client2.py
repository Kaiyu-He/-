import socket
import threading

HOST = '192.168.192.137'
PORT = 1234


def receive_messages(s):
    while True:
        # 接收回复
        data = s.recv(1024)
        if not data:
            break
        print(f"收到回复: {data.decode('utf-8')}")


def send_messages(s):
    while True:
        # 发送消息
        msg = input("输入消息: ")
        s.sendall(msg.encode('utf-8'))


def client():
    # 创建TCP套接字
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # 连接到目标服务器
        s.connect((HOST, PORT))
        print(f"已连接到服务器 {HOST}:{PORT}")

        # 创建并启动接收消息的线程
        receive_thread = threading.Thread(target=receive_messages, args=(s,))
        receive_thread.daemon = True
        receive_thread.start()

        # 在主线程中发送消息
        send_messages(s)


if __name__ == "__main__":
    client()
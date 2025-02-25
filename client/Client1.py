import socket
import threading
from Client import Client


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


def main(
    host='10.39.43.221',
    port=1234
):
    name = input("输入用户名：")
    client = Client(host, port, name)
    print("close")
    client.close()

if __name__ == "__main__":
    main()

import socket


class Client:  # 客户端
    def __init__(self, host: str, port: int, name: str):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((host, port))
        print(f"已连接到服务器 {host}:{port}")
        self.name = name  # 用户名称
        self.user_name(name)

    def user_name(self, name):
        self.send_msg(name)
        return

    def send_msg(self, msg: str):
        """
        发送消息
        :param msg: 要发送的消息（字符串）
        """
        self.conn.send(msg.encode('utf-8'))

    def read(self) -> str:
        """
        从客户端接收消息
        """
        msg = self.conn.recv(1024).decode('utf-8')
        return msg

    def close(self):
        self.conn.close()
        return
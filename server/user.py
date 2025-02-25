import socket


class User:  # 单个用户连接
    def __init__(self, conn: socket.socket, addr: tuple):
        """
        初始化用户连接
        :param conn: 客户端连接对象
        :param addr: 客户端地址和端口 (ip, port)
        """
        self.conn = conn  # 连接对象
        self.addr = f"{addr[0]}:{addr[1]}"  # 客户端地址:端口
        self.name = None  # 用户名称

    def get_user_name(self) -> tuple:
        """
        从客户端接收用户名
        :return: 用户名和客户端地址 (name, addr)
        """
        self.name = self.read()
        return self.name, self.addr

    def send(self, msg: str):
        """
        向客户端发送消息
        :param msg: 要发送的消息（字符串）
        """
        self.conn.send(msg.encode("utf-8"))

    def read(self) -> str:
        """
        从客户端接收消息
        """
        msg = self.conn.recv(1024).decode('utf-8')
        return msg

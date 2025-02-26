import json
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
    def close(self):
        self.conn.close()



class Server:
    def __init__(self, host: str, port: int, num_of_user: int):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen(num_of_user)
        self.users: dict[str: User] = {}
        self.online: dict[str: bool] = {}

    def add_user(self):
        conn, addr = self.server_socket.accept()
        user = User(conn, addr)
        name, addr = user.get_user_name()
        print(f"用户：{name} 登入, 地址{addr}")
        self.users[name] = user
        self.online[name] = True
        self.send_to_all(f"users_online:{json.dumps(self.online)}")
        return name, addr, user

    def send_to_users(self, name: str, msg: str):
        if name in self.users and self.online[name]:
            self.users[name].send(msg)

    def send_to_all(self, msg):
        for name, online in self.online.items():
            if online:
                self.send_to_users(name, msg)

    def user_close(self, name):
        self.online[name] = False
        user = self.users[name]
        print(f"用户：{user.name} 下线, 地址{user.addr}")
        self.users[name].close()
        self.send_to_all(f"users_online:{json.dumps(self.online)}")



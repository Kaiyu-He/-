import socket


class Client:  # 客户端
    def __init__(self, host: str, port: int, name: str):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((host, port))
        print(f"已连接到服务器 {host}:{port}")
        self.name = name  # 用户名称
        self.user_name(name)
        self.friends = {}

    def get_friends(self) -> list:
        users = []
        for user, msgs in self.friends.items():
            users.append(user)
        return users

    def get_user_msg(self, name) -> dict:
        if name not in self.friends:
            self.add_friend(name)
        return self.friends[name]['msg']


    def add_friend(self, name):
        if name not in self.friends:
            self.friends[name] = {
                "msg": []
            }

    def add_msg(self, name: str, msg: str):
        if name not in self.friends:
            self.add_friend(name)
        self.friends[name]['msg'].append(msg)

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
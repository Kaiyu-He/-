import json
import socket
import time


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
        self.max_length = 2 ** 30

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
        msg = self.conn.recv(self.max_length).decode('utf-8')
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
        self.history: dict[str: dict] = self.load_history()
        for user_name, value in self.history.items():
            self.online[user_name] = False
    def load_history(self):
        load_path = "./server_total_history_save.json"
        try:
            with open(load_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}

    def save_history(self):
        save_path = "./server_total_history_save.json"
        try:
            with open(save_path, "w") as f:
                f.write(json.dumps(self.history, indent=4, ensure_ascii=False))
        except Exception as e:
            print(f"无法保存: {e}")

    def add_user(self):
        conn, addr = self.server_socket.accept()
        user = User(conn, addr)
        name, addr = user.get_user_name()
        print(f"用户：{name} 登入, 地址{addr}")
        self.users[name] = user
        self.online[name] = True
        self.send_to_all(f"users_online:{json.dumps(self.online)}")
        if name not in self.history:
            self.history[name]: dict = {
                "type": "user",
                "history": {},
                "password": None
            }
        self.history[name]['history']['deepseek'] = {
            "msg": [],
        }
        time.sleep(0.5)
        self.send_to_users(name, f"users_history:{json.dumps(self.history[name]['history'])}")
        return name, addr, user

    def add_friend(self, from_user, to_user):
        if from_user not in self.history:
            ValueError("用户不存在")
        self.history[from_user]['history'][to_user] = {
            "msg": [],
            "user": None
        }

    def get_deepseek_chat(self, user_name, message):
        self.history[user_name]['history']['deepseek']['msg'].append(f"user:{message}")
        history = self.history[user_name]['history']['deepseek']['msg']
        message = []
        for sentence in history:
            message.append({"role": sentence.split(":", 1)[0], "content": sentence.split(":", 1)[1]})
        return message

    def add_deepseek_chat(self, user_name, deepseek_response):
        self.history[user_name]['history']['deepseek']['msg'].append(f"assistant:{deepseek_response}")

    def add_chat(self, from_user: str, to_user_or_group, message):
        if self.history[to_user_or_group]['type'] == "user":
            if to_user_or_group not in self.history[from_user]:
                self.add_friend(from_user, to_user_or_group)
            self.send_to_users(to_user_or_group, message)
            self.history[from_user]['history'][to_user_or_group]["msg"].append(message)
            self.history[to_user_or_group]['history'][from_user]["msg"].append(message)
        else:
            for group_user in self.history[to_user_or_group]["users_list"]:
                if group_user not in self.history:
                    continue
                self.history[group_user]['history'][to_user_or_group]['msg'].append(message)
                if group_user == from_user:
                    continue
                self.send_to_users(group_user, message)

    def add_group(self, from_user, group_name, users_list):
        group_name = group_name
        if group_name in self.history:
            if from_user not in self.history[group_name]["users_list"]:
                return None
            for add_user in users_list:
                if add_user not in self.history[group_name]["users_list"]:
                    self.history[group_name]["users_list"].append(add_user)
            return f"{from_user}/{self.history[group_name]['users_list']}/{group_name}"
        self.history[group_name] = {
            "type": f"group_[]",
            "users_list": users_list
        }
        for group_user in users_list:
            if group_user not in self.history:
                self.history[group_user]: dict = {
                    "type": "user",
                    "history": {}
                }
            self.history[group_user]['history'][group_name] = {
                "msg": [],
                "user": users_list
            }
        return f"{from_user}/{self.history[group_name]['users_list']}/{group_name}"

    def send_to_users(self, name: str, msg: str):
        self.save_history()
        if name in self.users and self.online[name]:
            print(f"发送信息给 {name}——{msg}")
            self.users[name].send(msg)

    def send_to_all(self, msg):
        for name, online in self.online.items():
            if online:
                self.send_to_users(name, msg)

    def user_close(self, name):
        self.online[name] = False
        user = self.users[name]
        print(f"用户：{user.name} 下线, 地址{user.addr}")
        self.history[name]['history']['deepseek']['msg'] = []
        self.users[name].close()
        self.send_to_all(f"users_online:{json.dumps(self.online)}")

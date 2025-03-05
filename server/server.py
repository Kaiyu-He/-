import ast
import json
import socket
import threading
import time

from user import User, Server
from openai import OpenAI


def deepseek(message):
    start = time.time()
    deepseek_api_key = "sk-a131ac41780f4ff8b63b4fd3698699f5"
    deepseek_model = OpenAI(api_key=deepseek_api_key, base_url="https://api.deepseek.com")
    response = deepseek_model.chat.completions.create(
        model="deepseek-chat",
        messages=message,
        stream=False,
    )
    text = response.choices[0].message.content
    print(f"deepseek_respoonse_time: {time.time() - start}")
    return text


def handle_users(server, user):
    while True:
        try:
            msg = user.read()
            if not msg:
                break
            msg_type, msg = msg.split(':', 1)
            print(f"收到用户信息 {user.addr}: 用户：{user.name}, 类型：{msg_type}, 内容：{msg}")
            if msg_type == 'message':
                args = msg.split('/', 2)
                if args[0] == args[1]:
                    continue
                if args[1] == "deepseek":
                    text = server.get_deepseek_chat(args[0], args[2])
                    text = deepseek(text)
                    message = f"message:deepseek/{args[0]}/{text}"
                    server.send_to_users(args[0], message)
                    server.add_deepseek_chat(args[0], text)
                else:
                    server.add_chat(args[0], args[1], f"message:{msg}")

            elif msg_type == 'add_group':
                args = msg.split('/')
                group_users = ast.literal_eval(args[1])
                msg = server.add_group(args[0], args[2], group_users)
                if msg is None:
                    continue
                for group_user in group_users:
                    if group_user == args[0]:
                        continue
                    server.send_to_users(group_user, f"add_group:{msg}")
            elif msg_type == 'add_friend':
                args = msg.split('/')
                server.add_friend(args[0], args[1])
            elif msg_type == "video":
                args = msg.split('/')
                server.send_to_users(args[1], f"video:{msg}")
            elif msg_type == "image":
                args = msg.split('/')
                server.send_to_users(args[1], f"image:{msg}")
        except Exception as e:
            print(f"Error with {user.addr}: {e}")
            break
    server.user_close(user.name)


def get_local_ipv4():
    try:
        # 创建一个 UDP 套接字
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 尝试连接到一个外部地址，这里使用 Google 的公共 DNS 服务器地址
        s.connect(("8.8.8.8", 80))
        # 获取本地 IP 地址
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        print(f"获取本地 IP 地址时出错: {e}")
        return None


# 启动服务器
def start_server(host=None, port=1234):
    if host == None:
        host = get_local_ipv4()

    server = Server(host, port, 20)
    print(f"服务器ip {host}:{port}")
    while True:
        name, addr, user = server.add_user()
        thread = threading.Thread(target=handle_users, args=(server, user))
        thread.start()


if __name__ == "__main__":
    start_server()

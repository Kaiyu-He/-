import ast
import json
import threading
from user import User, Server


def handle_users(server, user):
    while True:
        try:
            msg = user.read()
            if not msg:
                break
            msg_type, msg = msg.split(':', 1)
            print(f"收到用户信息 {user.addr}: 用户：{user.name}, 类型：{msg_type}, 内容：{msg}")
            if msg_type == 'message':
                args = msg.split('/')
                if args[0] == args[1]:
                    continue
                server.add_chat(args[0],args[1], f"message:{msg}")

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
        except Exception as e:
            print(f"Error with {user.addr}: {e}")
            break
    server.user_close(user.name)


# 启动服务器
def start_server(host="10.23.232.177", port=1234):
    server = Server(host, port, 20)
    print(f"服务器ip {host}:{port}")
    while True:
        name, addr, user = server.add_user()
        thread = threading.Thread(target=handle_users, args=(server, user))
        thread.start()


if __name__ == "__main__":
    start_server()

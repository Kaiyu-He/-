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
            print(f"收到用户信息 {user.addr}: 类型：{msg_type}, 内容：{msg}")
            if msg_type == 'message':
                from_user, to_user, text = msg.split('/')
                if from_user == to_user:
                    continue
                server.send_to_users(to_user, f"message:{msg}")
                print(f"发送信息给 {to_user}——message:{msg}")
        except Exception as e:
            print(f"Error with {user.addr}: {e}")
            break
    server.user_close(user.name)


# 启动服务器
def start_server(host="10.39.43.221", port=1234):
    server = Server(host, port, 20)
    print(f"服务器ip {host}:{port}")
    while True:
        name, addr, user = server.add_user()
        thread = threading.Thread(target=handle_users, args=(server, user))
        thread.start()


if __name__ == "__main__":
    start_server()


import threading
from user import User, Server


def handle_users(server, user):
    while True:
        try:
            msg = user.read()
            if not msg:
                break
            print(f"收到用户信息 {user.addr}: {msg}")
            name, text = msg.split(":", 1)
            server.send_to_users(name, text)
        except Exception as e:
            print(f"Error with {user.addr}: {e}")
            break
    server.user_close(user.name)

# 启动服务器
def start_server(host="10.24.8.39", port=1234):
    server = Server(host, port, 20)
    print(f"服务器ip {host}:{port}")
    while True:
        name, addr, user = server.add_user()
        thread = threading.Thread(target=handle_users, args=(server, user))
        thread.start()


if __name__ == "__main__":
    start_server()

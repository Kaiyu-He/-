import socket
import threading
from user import User
# 处理客户端连接的函数
def handle_client(conn, addr):
    while True:
        try:
            data = conn.recv(1024)  # 接收数据
            if not data:
                break  # 如果客户端关闭连接，退出循环
            print(f"Received from {addr}: {data.decode()}")
            conn.send(data)  # 将数据回显给客户端
        except Exception as e:
            print(f"Error with {addr}: {e}")
            break
    print(f"Connection from {addr} closed")
    conn.close()

# 启动服务器
def start_server(host="10.39.43.221", port=1234):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"服务器ip {host}:{port}")

    while True:
        conn, addr = server_socket.accept()
        user = User(conn, addr)
        name, addr = user.get_user_name()
        print(f"用户：{name} 登入, 地址{addr}")
        client_thread = threading.Thread(target=handle_client, args=(conn, addr))
        client_thread.start()

if __name__ == "__main__":
    start_server()
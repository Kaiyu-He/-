import sys
import socket

from PyQt6.QtWidgets import QApplication
from gui import ChatClient


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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    host = get_local_ipv4()
    port = 1234
    window = ChatClient(host, port)
    window.show()
    sys.exit(app.exec())
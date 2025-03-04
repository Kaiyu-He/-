import sys
import socket

from PyQt6.QtWidgets import QApplication
from gui import ChatClient



if __name__ == "__main__":
    print(get_local_ipv4())
    app = QApplication(sys.argv)
    host = '10.23.243.6'
    port = 1234
    window = ChatClient(host, port)
    window.show()
    sys.exit(app.exec())
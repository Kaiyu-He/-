import os
import sys
from PyQt6.QtWidgets import QApplication
from gui import ChatClient
os.chdir(os.path.dirname(__file__))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    host = '10.23.232.177'
    port = 1234
    window = ChatClient(host, port)
    window.show()
    sys.exit(app.exec())
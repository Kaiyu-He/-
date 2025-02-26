import sys
from PyQt6.QtWidgets import QApplication
from gui import ChatClient

if __name__ == "__main__":
    app = QApplication(sys.argv)
    host = '10.39.43.221'
    port = 1234
    window = ChatClient(host, port)
    window.show()
    sys.exit(app.exec())
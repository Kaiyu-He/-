import sys
import threading
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget,
    QTextEdit, QMessageBox, QInputDialog
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
from Client import Client


class ChatClient(QMainWindow):
    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.client = None
        self.friend = {}
        self.current_chat_box = None  # 当前显示的聊天框
        self.selected_user = None  # 当前选中的用户
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("聊天客户端")
        self.setGeometry(100, 100, 800, 600)

        # 创建登录界面
        self.login_widget = QWidget()
        self.login_layout = QVBoxLayout()
        self.login_widget.setLayout(self.login_layout)

        self.name_label = QLabel("输入用户名：")
        self.login_layout.addWidget(self.name_label)

        self.name_input = QLineEdit()
        self.login_layout.addWidget(self.name_input)

        self.start_button = QPushButton("开始聊天")
        self.start_button.clicked.connect(self.start_chat)
        self.login_layout.addWidget(self.start_button)

        self.setCentralWidget(self.login_widget)

    def start_chat(self):
        """开始聊天"""
        name = self.name_input.text()
        if name:
            try:
                self.client = Client(self.host, self.port, name)
                self.show_chat_interface()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"连接服务器失败: {e}")

    def show_chat_interface(self):
        """显示聊天界面"""
        self.login_widget.hide()

        # 创建主聊天界面
        self.chat_widget = QWidget()
        self.chat_layout = QHBoxLayout()
        self.chat_widget.setLayout(self.chat_layout)

        # 左侧用户列表
        self.user_list_widget = QListWidget()
        self.user_list_widget.itemClicked.connect(self.on_user_select)
        self.chat_layout.addWidget(self.user_list_widget)

        # 右侧聊天框和输入框
        self.right_widget = QWidget()
        self.right_layout = QVBoxLayout()
        self.right_widget.setLayout(self.right_layout)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.right_layout.addWidget(self.chat_display)

        self.input_field = QLineEdit()
        self.input_field.returnPressed.connect(self.send_msg)
        self.right_layout.addWidget(self.input_field)

        self.send_button = QPushButton("发送")
        self.send_button.clicked.connect(self.send_msg)
        self.right_layout.addWidget(self.send_button)

        self.add_friend_button = QPushButton("添加好友")
        self.add_friend_button.clicked.connect(self.add_friend)
        self.right_layout.addWidget(self.add_friend_button)

        self.chat_layout.addWidget(self.right_widget)
        self.setCentralWidget(self.chat_widget)

        # 启动接收消息的线程
        self.receive_thread = threading.Thread(target=self.receive_msg)
        self.receive_thread.daemon = True
        self.receive_thread.start()

        # 使用 QTimer 定期更新聊天界面
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_chat_display)
        self.timer.start(200)  # 每1秒更新一次

    def receive_msg(self):
        """接收消息"""
        while True:
            try:
                msg = self.client.read()
                name, _ = msg.split('/', 1)
                if name == self.selected_user:
                    self.add_chat_display(msg)
                else:
                    self.update_chat_display()  # 更新聊天框
            except Exception as e:
                print(f"接收消息出错: {e}")
                break

    def send_msg(self):
        """发送消息"""
        msg = self.input_field.text()
        if msg and self.selected_user:
            try:
                msg = f"{self.selected_user}/{msg}"
                self.client.add_msg(self.selected_user, msg)
                self.add_chat_display(msg)
                self.client.send_msg(msg)
                self.chat_display.append(f"你向 {self.selected_user} 发送了：{msg}")
                self.input_field.clear()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"发送消息失败: {e}")

    def on_user_select(self, item):
        """切换用户时更新聊天框"""
        self.selected_user = item.text()
        self.update_chat_display()

    def add_friend(self):
        """添加好友"""
        friend_name, ok = QInputDialog.getText(self, "添加好友", "请输入好友的用户名:")
        if ok and friend_name:
            try:
                self.client.add_friend(friend_name)
                self.update_friends_list()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"添加好友失败: {e}")

    def update_friends_list(self):
        """更新好友列表"""
        if self.client:
            friends = self.client.get_friends()
            self.user_list_widget.clear()
            for friend in friends:
                self.user_list_widget.addItem(friend)

    def update_chat_display(self):
        """更新聊天框"""
        if self.selected_user and self.client:
            messages = self.client.get_msg(self.selected_user)
            self.chat_display.clear()
            for message in messages:
                self.add_chat_display(message)
    def add_chat_display(self, msg: str):
        msg = msg.split('/')
        self.chat_display.append(f"{msg[0]}: {msg[1]}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    host = '10.24.8.39'
    port = 1234
    window = ChatClient(host, port)
    window.show()
    sys.exit(app.exec())
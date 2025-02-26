import json
import threading
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget,
    QTextEdit, QMessageBox, QInputDialog, QDialog, QListWidget, QVBoxLayout, QHBoxLayout, QDialogButtonBox,
    QListWidgetItem
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
from Client import Client


class AddFriendDialog(QDialog):
    """自定义添加好友对话框，带搜索框"""

    def __init__(self, parent=None, user: str = None):
        super().__init__(parent)
        self.setWindowTitle("添加好友")
        self.setGeometry(100, 100, 300, 200)
        self.user = user
        # 主布局
        layout = QVBoxLayout(self)

        # 搜索框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索好友...")
        self.search_input.textChanged.connect(self.filter_friends)
        layout.addWidget(self.search_input)

        # 好友列表
        self.friend_list = QListWidget()
        layout.addWidget(self.friend_list)

        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def filter_friends(self):
        """根据搜索框内容过滤好友列表"""
        search_text = self.search_input.text().lower()
        for i in range(self.friend_list.count()):
            item = self.friend_list.item(i)
            item.setHidden(search_text not in item.text().lower())

    def set_friends(self, friends):
        """设置好友列表，显示在线状态和颜色"""
        self.friend_list.clear()
        for friend, online in friends.items():
            if friend == self.user:
                continue
            # 创建一个 QWidget 作为容器
            widget = QWidget()
            layout = QHBoxLayout(widget)  # 使用水平布局

            # 用户名标签（靠左）
            username_label = QLabel(friend)
            username_label.setStyleSheet("color: black;")  # 用户名颜色为黑色
            layout.addWidget(username_label)

            status_label = QLabel("在线" if online else "离线")
            status_label.setStyleSheet("color: green;" if online else "color: gray;")  # 在线为绿色，离线为灰色
            layout.addWidget(status_label)

            # 设置布局的对齐方式
            layout.addStretch()  # 将用户名推到左边，状态推到右边

            # 创建 QListWidgetItem
            item = QListWidgetItem()
            item.setSizeHint(widget.sizeHint())  # 设置项的大小

            self.friend_list.addItem(item)
            self.friend_list.setItemWidget(item, widget)

    def get_selected_friend(self):
        """获取选中的好友"""
        selected_items = self.friend_list.selectedItems()
        if selected_items:
            item = selected_items[0]
            widget = self.friend_list.itemWidget(item)
            if widget:
                username_label = widget.layout().itemAt(0).widget()
                return username_label.text()
        return None


class ChatClient(QMainWindow):
    message_received = pyqtSignal(str)

    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.client = None
        self.friend = {}
        self.online = {}
        self.current_chat_box = None
        self.selected_user = None
        self.init_ui()
        self.message_received.connect(self.handle_message)

    def handle_message(self, msg):
        try:
            if ':' not in msg:
                raise ValueError("消息格式错误")
            msg_type, msg = msg.split(':', 1)
            if msg_type == "message":
                if '/' not in msg:
                    raise ValueError("消息格式错误")
                parts = msg.split('/')
                if len(parts) != 3:
                    raise ValueError("消息格式错误")
                from_user, to_user, text = parts
                self.client.add_friend(from_user)
                self.update_friends_list()
                self.client.add_msg(from_user, f"message:{msg}")
                self.update_chat_display()
            elif msg_type == 'users_online':
                self.online = json.loads(msg)
        except Exception as e:
            print(f"处理消息出错: {e}")

    def receive_msg(self):
        """接收消息的线程函数"""
        while True:
            try:
                msg = self.client.read()
                self.message_received.emit(msg)  # 发射信号
            except Exception as e:
                print(f"接收消息出错: {e}")
                break

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
        if ' ' in name:
            QMessageBox.warning(self, "错误", "用户名不能包含空格，请重新输入。")
            return
        if len(name) >= 15:
            QMessageBox.warning(self, "错误", "用户名长度不得大于15，请重新输入。")
            return
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

    def send_msg(self):
        """发送消息"""
        msg = self.input_field.text()
        if msg and self.selected_user:
            try:
                msg = f"message:{self.client.name}/{self.selected_user}/{msg}"
                self.client.add_msg(self.selected_user, msg)
                self.add_chat_display(f"{self.client.name}/{self.selected_user}/{msg}")
                self.client.send_msg(msg)
                self.input_field.clear()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"发送消息失败: {e}")



    def add_friend(self):
        dialog = AddFriendDialog(self, user=self.client.name)
        dialog.set_friends(self.online)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_friend = dialog.get_selected_friend()
            if selected_friend:
                try:
                    self.client.add_friend(selected_friend)
                    self.update_friends_list()

                    # 设置新添加的好友为默认选项
                    self.selected_user = selected_friend
                    self.update_chat_display()

                    # 选中好友列表中的新好友
                    items = self.user_list_widget.findItems(selected_friend, Qt.MatchFlag.MatchExactly)
                    if items:
                        self.user_list_widget.setCurrentItem(items[0])
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"添加好友失败: {e}")

    def update_friends_list(self):

        """更新好友列表，显示用户名和在线状态"""
        friends = self.client.get_friends()  # 获取好友列表
        self.user_list_widget.clear()  # 清空当前列表

        for friend in friends:
            # 获取好友的在线状态（假设 self.online 是一个字典，键为好友名字，值为在线状态）
            online = self.online.get(friend, False)

            # 创建一个 QWidget 作为容器
            widget = QWidget()
            layout = QHBoxLayout(widget)  # 使用水平布局

            # 用户名标签（靠左）
            username_label = QLabel(friend)
            username_label.setStyleSheet("color: black;")  # 用户名颜色为黑色
            layout.addWidget(username_label)

            # 在线状态标签（靠右）
            status_label = QLabel("在线" if online else "离线")
            status_label.setStyleSheet("color: green;" if online else "color: gray;")  # 在线为绿色，离线为灰色
            layout.addWidget(status_label)

            # 设置布局的对齐方式
            layout.addStretch()  # 将用户名推到左边，状态推到右边

            # 创建 QListWidgetItem
            item = QListWidgetItem()
            item.setSizeHint(widget.sizeHint())  # 设置项的大小

            # 将 QWidget 添加到 QListWidgetItem
            self.user_list_widget.addItem(item)
            self.user_list_widget.setItemWidget(item, widget)

            widget.setFixedHeight(40)  # 设置每个列表项的高度为 40 像素
            username_label.setFixedHeight(30)  # 设置用户名标签的高度为 30 像素
            status_label.setFixedHeight(30)  # 设置状态标签的高度为 30 像素
    def on_user_select(self, item):
        """切换用户时更新聊天框"""
        # 获取选中的 QListWidgetItem
        selected_item = self.user_list_widget.itemWidget(item)
        if selected_item:
            # 从 QWidget 中获取用户名标签的文本
            username_label = selected_item.layout().itemAt(0).widget()
            self.selected_user = username_label.text()
            self.update_chat_display()


    def update_chat_display(self):
        """更新聊天框"""
        if self.selected_user and self.client:
            print("start select")
            messages = self.client.get_user_msg(self.selected_user)
            print(f"get message {messages}")
            self.chat_display.clear()
            for message in messages:
                self.add_chat_display(message)
            print("finish")

    def add_chat_display(self, msg: str):
        """添加聊天框信息"""
        print(f"msg:{msg}")
        msg_type, msg = msg.split(':', 1)
        print(msg)
        msg = msg.split('/')
        self.chat_display.append(f"{msg[0]}: {msg[2]}")

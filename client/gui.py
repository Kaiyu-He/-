import ast
import json
import os.path
import socket
import tempfile
import threading
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget,
    QTextEdit, QMessageBox, QInputDialog, QDialog, QListWidget, QVBoxLayout, QHBoxLayout, QDialogButtonBox,
    QListWidgetItem, QGraphicsDropShadowEffect, QFileDialog
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
from Client import Client

from addfriend import AddFriendDialog, AddGroupFriendDialog
from ui.log_in import Ui_login
from ui.chat import Ui_MainWindow as UI_chat
from video import VideoAudioDialog


class TextEditWithEnter(QTextEdit):
    def __init__(self, process_enter, parent=None):
        super().__init__(parent)
        self.process = process_enter

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return and event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            # 如果按下 Shift + Enter，插入换行
            self.insertPlainText("\n")
        elif event.key() == Qt.Key.Key_Return:
            # 如果按下 Enter，发送内容
            self.process()
        else:
            # 其他按键按默认处理
            super().keyPressEvent(event)


class ChatClient(QMainWindow, Ui_login, UI_chat):
    message_received = pyqtSignal(str)

    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.ipv4 = get_local_ipv4()
        self.client = None
        self.online = {}
        self.current_chat_box = None
        self.selected_user = None
        self.video_port = 12654
        self.init_ui()
        self.message_received.connect(self.handle_message)

    def handle_message(self, msg):
        try:
            if ':' not in msg:
                raise ValueError(f"消息格式错误: {msg}")
            msg_type, msg = msg.split(':', 1)
            if msg_type == "message":
                try:
                    parts = msg.split('/', 2)
                except:
                    raise ValueError("消息格式错误")
                from_user, to_user, text = parts
                if to_user == self.client.name:
                    self.client.add_chat(from_user)
                    self.update_friends_list()
                    self.client.add_msg(from_user, f"message:{msg}")
                    self.update_chat_display()
                else:
                    self.client.add_chat(to_user)
                    self.update_friends_list()
                    self.client.add_msg(to_user, f"message:{msg}")
                    self.update_chat_display()
            elif msg_type == 'users_online':
                self.online = json.loads(msg)
                self.update_friends_list()
            elif msg_type == "add_group":
                args = msg.split('/')
                group_users = ast.literal_eval(args[1])
                self.client.add_chat(args[2], group_users)
                self.update_friends_list()
            elif msg_type == "users_history":
                self.client.friends = json.loads(msg)
                for user_name, history in self.client.friends.items():
                    self.selected_user = user_name
                    break
                self.update_friends_list()
                self.update_chat_display()
            elif msg_type == "video":
                args = msg.split('/')
                self.video.clicked.disconnect(self.start_video)
                dialog = VideoAudioDialog(args[2], int(args[3]), False)
                dialog.show()
                self.video.clicked.connect(self.start_video)
                dialog.exec()
        except Exception as e:
            print(f"处理消息出错: {e} {msg}")

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
        self.setupUi_login(self)
        self.start_button.clicked.connect(self.start_chat)

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

        self.setupUi(self, name=self.client.name)

        self.add_group_button.clicked.connect(self.add_group)
        self.user_list_widget.itemClicked.connect(self.on_user_select)

        self.chat_display.setReadOnly(True)

        index = self.right_widge.indexOf(self.input_field)
        stretch = self.right_widge.stretch(index)
        self.right_widge.removeWidget(self.input_field)
        self.input_field.deleteLater()
        new_input_field = TextEditWithEnter(self.send_msg)
        new_input_field.setObjectName("input_field")  # 保持相同的对象名
        self.right_widge.insertWidget(index, new_input_field)
        self.right_widge.setStretch(index, stretch)
        self.input_field = new_input_field

        # self.input_field.returnPressed.connect(self.send_msg)
        # self.input_field.setFixedHeight(20)
        self.send_button.clicked.connect(self.send_msg)
        self.add_friend_button.clicked.connect(self.add_friend)

        self.video.clicked.connect(self.start_video)
        self.image.clicked.connect(self.send_image)
        # 启动接收消息的线程
        self.receive_thread = threading.Thread(target=self.receive_msg)
        self.receive_thread.daemon = True
        self.receive_thread.start()

    def send_msg(self):
        """发送消息"""
        msg = self.input_field.toPlainText()
        if msg and self.selected_user:
            try:
                text = f"message:{self.client.name}/{self.selected_user}/{msg}"
                self.add_chat_display(text)
                self.client.add_msg(self.selected_user, text)
                self.client.send_msg(text)
                self.input_field.clear()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"发送消息失败: {e}")

    def add_group(self):
        """添加群聊"""
        dialog = AddGroupFriendDialog(self, user=self.client.name)
        # dialog.set_friends(self.online)
        # if dialog.exec() == QDialog.DialogCode.Accepted:
        group_name, selected_friends = dialog.get_selected_friends()
        if self.client.name not in selected_friends:
            selected_friends.append(self.client.name)
        msg = f"add_group:{self.client.name}/{selected_friends}/{group_name}"
        self.client.add_chat(group_name, selected_friends)
        self.update_friends_list()

        self.selected_user = group_name
        self.update_chat_display()

        items = self.user_list_widget.findItems(group_name, Qt.MatchFlag.MatchExactly)
        if items:
            self.user_list_widget.setCurrentItem(items[0])
        self.client.send_msg(msg)

    def add_friend(self):
        dialog = AddFriendDialog(self, user=self.client.name)
        dialog.set_friends(self.online)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_friend = dialog.get_selected_friend()
            if selected_friend:
                try:
                    self.client.add_chat(selected_friend)
                    self.update_friends_list()

                    # 设置新添加的好友为默认选项
                    self.selected_user = selected_friend
                    self.update_chat_display()

                    # 选中好友列表中的新好友
                    items = self.user_list_widget.findItems(selected_friend, Qt.MatchFlag.MatchExactly)
                    if items:
                        self.user_list_widget.setCurrentItem(items[0])
                    self.client.send_msg(f"add_friend:{self.client.name}/{selected_friend}")
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"添加好友失败: {e}")

    def send_image(self):
        """发送图片"""
        if self.selected_user:
            # 打开文件选择对话框
            file_path, _ = QFileDialog.getOpenFileName(self, "选择图片文件", "", "图片文件 (*.png *.jpg *.jpeg)")
            if file_path:
                try:
                    # 读取图片文件内容
                    with open(file_path, 'rb') as f:
                        file_data = f.read()
                    file_name = file_path.split('/')[-1]
                    # 构造图片消息
                    text = f"message:{self.client.name}/{self.selected_user}/<|image|>{file_data.decode('latin1')}<|end_image|>"
                    self.client.send_msg(text)
                    self.client.add_chat(self.selected_user)
                    self.update_friends_list()
                    self.client.add_msg(self.selected_user, text)
                    self.update_chat_display()
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"发送图片失败: {e}")

    def start_video(self):
        self.video.clicked.disconnect(self.start_video)
        try:
            if self.selected_user in self.online and \
                    self.online[self.selected_user] and self.selected_user != self.client.name:
                self.client.send_msg(f"video:{self.client.name}/{self.selected_user}/{self.ipv4}/{self.video_port}")
                dialog = VideoAudioDialog(self.ipv4, self.video_port, True)
                dialog.exec()
        except Exception as e:
            print(f"视频连接失败 {e}")
        self.video.clicked.connect(self.start_video)

    def update_friends_list(self):

        """更新好友列表，显示用户名和在线状态"""
        friends = self.client.get_chats()  # 获取好友列表
        self.user_list_widget.clear()  # 清空当前列表

        for friend in friends:
            # 获取好友的在线状态（假设 self.online 是一个字典，键为好友名字，值为在线状态）
            # 创建一个 QWidget 作为容器
            widget = QWidget()
            layout = QHBoxLayout(widget)  # 使用水平布局

            # 用户名标签（靠左）
            username_label = QLabel(friend)
            username_label.setStyleSheet("color: black;")  # 用户名颜色为黑色
            layout.addWidget(username_label)

            if friend in self.online:
                online = self.online[friend]
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
            if friend == self.selected_user:
                widget.setStyleSheet("background-color: #d4d4d4;")
            username_label.setFixedHeight(30)  # 设置用户名标签的高度为 30 像素
            try:
                status_label.setFixedHeight(30)  # 设置状态标签的高度为 30 像素
            except:
                continue

    def on_user_select(self, item):
        """切换用户时更新聊天框"""
        # 获取选中的 QListWidgetItem
        selected_item = self.user_list_widget.itemWidget(item)
        if selected_item:
            # 从 QWidget 中获取用户名标签的文本
            username_label = selected_item.layout().itemAt(0).widget()
            self.selected_user = username_label.text()
            self.update_chat_display()
            self.update_friends_list()

    def update_chat_display(self):
        """更新聊天框"""
        text = self.selected_user
        self.name_chat.setText(text)
        if self.selected_user and self.client:
            messages = self.client.get_user_msg(self.selected_user)
            self.chat_display.clear()
            for message in messages:
                self.add_chat_display(message)

    def add_chat_display(self, msg: str):
        """添加聊天框信息"""
        try:
            msg_type, msg = msg.split(':', 1)
            parts = msg.split('/', 2)
            from_user, _, content = parts
            if "<|image|>" in content and "<|end_image|>" in content:
                # 处理图片消息
                start_index = content.index("<|image|>") + len("<|image|>")
                end_index = content.index("<|end_image|>")
                image_data = content[start_index:end_index].encode('latin1')
                # 创建临时文件保存图片
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                    temp_file.write(image_data)
                    temp_file_path = temp_file.name
                # 在 chat_display 中插入图片
                html = f'<p>{from_user}:<img src="{temp_file_path}" width="100"></p>'
            else:
                html = f"""
                <div style="background-color: #dcf8c6; border-radius: 10px 10px 0 10px; padding: 10px; margin-bottom: 10px; max-width: 70%; float: right; clear: both;">
                    <span style="font-weight: bold; color: #25d366;">{from_user}</span>: <span style="color: #37474f;">{msg}</span>
                </div>
                """
            self.chat_display.insertHtml(html)
        except Exception as e:
            print(f"显示消息出错: {e} {msg}")



def get_local_ipv4():
    try:
        # 创建一个 UDP 套接字
        s_get_ip = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 尝试连接到一个外部地址，这里使用 Google 的公共 DNS 服务器地址
        s_get_ip.connect(("8.8.8.8", 80))
        # 获取本地 IP 地址
        local_ip = s_get_ip.getsockname()[0]
        s_get_ip.close()
        return local_ip
    except Exception as e:
        print(f"获取本地 IP 地址时出错: {e}")
        return None

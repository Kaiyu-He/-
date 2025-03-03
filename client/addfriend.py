from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QDialog, QListWidget, QVBoxLayout, QHBoxLayout, \
    QDialogButtonBox, QListWidgetItem, QAbstractItemView

class AddGroupFriendDialog(QDialog):
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
        """设置好友列表，显示在线状态和颜色，并添加复选框"""
        self.friend_list.clear()
        for friend, online in friends.items():

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
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)  # 启用复选框
            item.setCheckState(Qt.CheckState.Unchecked)  # 默认未选中
            item.setSizeHint(widget.sizeHint())  # 设置项的大小

            self.friend_list.addItem(item)
            self.friend_list.setItemWidget(item, widget)

    def get_selected_friends(self):
        """获取选中的好友列表（带复选框的选中状态）"""
        return "group", ['hekaiyu', "111", "he"]


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
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QDialog, QListWidget, QVBoxLayout, QHBoxLayout, \
    QDialogButtonBox, QListWidgetItem, QAbstractItemView, QTableWidgetItem, QHeaderView

from  ui.GroupChat import Ui_Dialog

class AddGroupFriend(QDialog):
    """自定义添加好友对话框，带搜索框"""

    def __init__(self, parent=None, contacts=None):
        super(AddGroupFriend, self).__init__(parent)
        self.ui = Ui_Dialog()

        self.ui.setupUi(self)
        self.ui.pBtnFinish.clicked.connect(self.CancelWindow)

        self.group_name = ""
        self.contacts = contacts or []

        self.load_contacts()

        header = self.ui.tableWidgetContacts.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.ui.tableWidgetContacts.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.ui.tableWidgetContacts.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        self.ui.lineEditSearch.textChanged.connect(self.search_contacts)
        self.ui.lineEditGroupName.textChanged.connect(self.update_group_name)

    def load_contacts(self):
        self.ui.tableWidgetContacts.setRowCount(len(self.contacts))
        self.ui.tableWidgetContacts.setColumnCount(1)
        self.ui.tableWidgetContacts.setHorizontalHeaderLabels(["联系人"])

        for row, contact in enumerate(self.contacts):
            item = QTableWidgetItem(contact)
            self.ui.tableWidgetContacts.setItem(row, 0, item)
    def search_contacts(self):
        """搜索联系人，在 QTableWidget 里筛选匹配项"""
        search_text = self.ui.lineEditSearch.text().strip().lower()  # 获取搜索框内容（忽略大小写）
        row_count = self.ui.tableWidgetContacts.rowCount()

        for row in range(row_count):
            item = self.ui.tableWidgetContacts.item(row, 0)  # 获取第 0 列的联系人
            if item:
                contact_name = item.text().strip().lower()
                match = search_text in contact_name  # 检查是否匹配搜索内容
                self.ui.tableWidgetContacts.setRowHidden(row, not match)  # 隐藏不匹配的行
    def CancelWindow(self):
        self.accept()
    def update_group_name(self):
        self.group_name = self.ui.lineEditGroupName.text()
    def get_group_name(self):
        return self.group_name
    def get_selected_contacts(self):
        """获取选中的联系人"""
        selected_contacts = []
        for item in self.ui.tableWidgetContacts.selectedItems():
            row = item.row()
            # 假设联系人名称在第一列
            contact_name = self.ui.tableWidgetContacts.item(row, 0).text()
            if contact_name not in selected_contacts:
                selected_contacts.append(contact_name)
        return selected_contacts


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
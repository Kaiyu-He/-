import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton, QGridLayout, QScrollArea
from PyQt6.QtCore import Qt

# 定义一些常用的 Unicode 表情
EMOJIS = [
    "😀", "😃", "😄", "😁", "😆", "😅", "😂", "🤣",
    "🥲", "😊", "😇", "🙂", "🙃", "😉", "😌", "😍",
    "🥰", "🤩", "🥳", "😎", "🤓", "🧐", "🤠", "🥸",
    "🤗", "🤔", "🤨", "😐", "😑", "😶", "😏", "😒",
    "🙄", "😬", "🤥", "😌", "😔", "😢", "😭", "😱",
    "😨", "😰", "😥", "😓", "🤗", "🤔", "🤨", "😐"
]


class EmojiFloatWindow(QWidget):
    def __init__(self, text_edit):
        super().__init__()
        self.text_edit = text_edit
        self.initUI()

    def initUI(self):
        # 创建表情按钮布局
        emoji_layout = QGridLayout()
        # 设置表情布局的水平和垂直间距为 0，让表情按钮紧密排列
        emoji_layout.setHorizontalSpacing(0)
        emoji_layout.setVerticalSpacing(0)
        emoji_layout.setContentsMargins(0, 0, 0, 0)

        row, col = 0, 0
        # 设置表情按钮的大小
        emoji_size = 35  # 可以根据需要调整表情按钮的大小
        # 设置表情字体样式
        font_size = 20  # 可以根据需要调整字体大小
        font_family = "Segoe UI Emoji"  # 可以根据需要调整字体家族
        font_style = f"font-family: {font_family}; font-size: {font_size}px; border: none;"

        for emoji in EMOJIS:
            # 创建表情按钮
            emoji_button = QPushButton(emoji)
            # 设置按钮的固定大小，使其更加紧凑
            emoji_button.setFixedSize(emoji_size, emoji_size)
            # 设置按钮的字体样式
            emoji_button.setStyleSheet(font_style)
            emoji_button.clicked.connect(lambda _, e=emoji: self.insert_emoji(e))
            emoji_layout.addWidget(emoji_button, row, col)
            col += 1
            if col == 8:  # 每行显示 8 个表情
                col = 0
                row += 1

        # 创建一个 QWidget 来容纳表情布局
        emoji_widget = QWidget()
        emoji_widget.setLayout(emoji_layout)

        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(emoji_widget)
        # 设置滚动区域的固定高度和宽度
        scroll_area.setFixedHeight(150)  # 可以根据需要调整滚动区域的高度
        scroll_area.setFixedWidth(emoji_size * 8 + 20)  # 根据表情按钮大小和每行显示数量计算滚动区域宽度

        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)

        # 设置窗口为无边框、置顶且透明背景
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def insert_emoji(self, emoji):
        # 获取当前文本输入框的光标位置
        cursor = self.text_edit.textCursor()
        # 在光标位置插入表情
        cursor.insertText(emoji)
        # 更新文本输入框的光标
        self.text_edit.setTextCursor(cursor)
        self.hide()


class EmojiApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 创建主垂直布局
        main_layout = QVBoxLayout()
        # 设置主布局的间距为 0，减少整体布局的空白
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 创建文本输入框
        self.text_edit = QTextEdit()
        main_layout.addWidget(self.text_edit)

        # 创建表情选择按钮
        self.emoji_button = QPushButton("😀")
        self.emoji_button.clicked.connect(self.show_emoji_window)
        main_layout.addWidget(self.emoji_button)

        # 创建表情浮窗
        self.emoji_window = EmojiFloatWindow(self.text_edit)

        # 设置主布局
        self.setLayout(main_layout)
        self.setWindowTitle('Emoji App')
        self.setGeometry(300, 300, 400, 400)
        self.show()

    def show_emoji_window(self):
        # 获取按钮在屏幕上的位置
        button_pos = self.emoji_button.mapToGlobal(self.emoji_button.pos())
        # 获取按钮的宽度和高度
        button_width = self.emoji_button.width()
        button_height = self.emoji_button.height()
        # 获取浮窗的宽度和高度
        window_width = self.emoji_window.width()
        window_height = self.emoji_window.height()
        # 计算浮窗的位置，使其显示在按钮的上方并居中
        x = button_pos.x() + (button_width - window_width) // 2
        y = button_pos.y() - window_height
        # 设置浮窗的位置
        self.emoji_window.move(x, y)
        self.emoji_window.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = EmojiApp()
    sys.exit(app.exec())
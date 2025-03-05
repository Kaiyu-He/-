from PIL import Image
from PyQt6 import QtGui
from PyQt6.QtCore import QSize, pyqtSignal, Qt, QThread
from PyQt6.QtGui import QPainter, QFont, QColor, QPixmap, QPolygon, QFontMetrics
from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QSizePolicy, QVBoxLayout, QSpacerItem, \
    QScrollArea, QScrollBar, QApplication


# 定义消息类型枚举
class MessageType:
    Text = 1
    Image = 2


# 头像组件类
class Avatar(QLabel):
    def __init__(self, avatar, text="", parent=None):
        super().__init__(parent)
        self.text = avatar  # 正确赋值文本信息
        if isinstance(avatar, str) and '.' in avatar:
            # 从文件路径加载头像并缩放
            self.setPixmap(QPixmap(avatar).scaled(45, 45))
            self.image_path = avatar
        elif isinstance(avatar, QPixmap):
            # 直接使用 QPixmap 对象并缩放
            self.setPixmap(avatar.scaled(45, 45))
        # 设置固定大小
        self.setFixedSize(QSize(45, 45))

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.text:
            painter = QPainter(self)
            # 设置字体
            font = QFont('Arial', 10)
            painter.setFont(font)
            # 设置文本颜色
            painter.setPen(QColor('black'))
            # 计算文本绘制的矩形区域，实现居中显示
            text_rect = self.rect()
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, self.text)
            painter.end()


# 消息气泡的三角箭头组件类
class Triangle(QLabel):
    def __init__(self, Type, is_send=False, parent=None):
        super().__init__(parent)
        self.Type = Type
        self.is_send = is_send
        # 设置固定大小
        self.setFixedSize(6, 45)

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        super(Triangle, self).paintEvent(a0)
        if self.Type == MessageType.Text:
            painter = QPainter(self)
            triangle = QPolygon()
            if self.is_send:
                # 设置发送消息三角箭头的颜色
                painter.setPen(QColor('#b2e281'))
                painter.setBrush(QColor('#b2e281'))
                # 定义发送消息三角箭头的顶点
                triangle.setPoints(0, 20, 0, 35, 6, 27)
            else:
                # 设置接收消息三角箭头的颜色
                painter.setPen(QColor('white'))
                painter.setBrush(QColor('white'))
                # 定义接收消息三角箭头的顶点
                triangle.setPoints(0, 27, 6, 20, 6, 35)
            # 绘制三角箭头
            painter.drawPolygon(triangle)


# 文本消息组件类
class TextMessage(QLabel):
    heightSingal = pyqtSignal(int)

    def __init__(self, text, is_send=False, parent=None):
        super(TextMessage, self).__init__(text, parent)
        font = QFont('微软雅黑', 10)
        self.setFont(font)
        # 设置自动换行
        self.setWordWrap(True)
        # 设置最大宽度
        self.setMaximumWidth(800)
        # 设置最小宽度
        self.setMinimumWidth(50)
        # 设置最小高度
        self.setMinimumHeight(45)
        # 设置文本可通过鼠标选择
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        # 设置大小策略
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        if is_send:
            # 设置发送消息的对齐方式和样式
            self.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignRight)
            self.setStyleSheet(
                '''
                background-color:#b2e281;
                border-radius:10px;
                border-top: 10px solid #b2e281;
                border-bottom: 10px solid #b2e281;
                border-right: 10px solid #b2e281;
                border-left: 10px solid #b2e281;
                '''
            )
        else:
            # 设置接收消息的样式
            self.setStyleSheet(
                '''
                background-color:white;
                border-radius:10px;
                border-top: 10px solid white;
                border-bottom: 10px solid white;
                border-right: 10px solid white;
                border-left: 10px solid white;
                '''
            )
        font_metrics = QFontMetrics(font)
        rect = font_metrics.boundingRect(text)
        # 根据文本内容调整最大宽度
        self.setMaximumWidth(rect.width() + 30)


# 图片消息组件类
class ImageMessage(QLabel):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            # 缩放图片并保持比例
            pixmap = pixmap.scaledToWidth(70, Qt.TransformationMode.SmoothTransformation)
            self.setPixmap(pixmap)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)


# 消息气泡组件类
class BubbleMessage(QWidget):
    def __init__(self, str_content, avatar, Type, is_send=False, parent=None):
        super().__init__(parent)
        self.isSend = is_send
        # 设置样式
        self.setStyleSheet(
            '''
            border:none;
            '''
        )
        layout = QHBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 5, 5, 5)

        self.avatar = Avatar(avatar)
        triangle = Triangle(Type, is_send)
        if Type == MessageType.Text:
            self.message = TextMessage(str_content, is_send)
        elif Type == MessageType.Image:
            self.message = ImageMessage(str_content)
        else:
            raise ValueError("未知的消息类型")

        self.spacerItem = QSpacerItem(45 + 6, 45, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        if is_send:
            # 发送消息的布局
            layout.addItem(self.spacerItem)
            layout.addWidget(self.message, 1)
            layout.addWidget(triangle, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
            layout.addWidget(self.avatar, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        else:
            # 接收消息的布局
            layout.addWidget(self.avatar, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
            layout.addWidget(triangle, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
            layout.addWidget(self.message, 1)
            layout.addItem(self.spacerItem)
        self.setLayout(layout)


# 主窗口类，用于测试消息气泡组件
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # 添加一些测试消息
        avatar_path = "avatar"  # 请替换为实际的头像图片路径
        text_message = BubbleMessage("这是一条文本消息", avatar_path, MessageType.Text, is_send=False)
        scroll_layout.addWidget(text_message)
        text_message = BubbleMessage("这是一条文本消息", avatar_path, MessageType.Text, is_send=True)
        scroll_layout.addWidget(text_message)

        image_message = BubbleMessage("./image/video.png", avatar_path, MessageType.Image, is_send=True)
        scroll_layout.addWidget(image_message)

        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
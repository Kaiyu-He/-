from PyQt6.QtWidgets import QTextEdit


class TextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return and event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            # 如果按下 Shift + Enter，插入换行
            self.insertPlainText("\n")
        elif event.key() == Qt.Key.Key_Return:
            # 如果按下 Enter，发送内容
            self.send_text()
        else:
            # 其他按键按默认处理
            super().keyPressEvent(event)

    def send_text(self):
        # 获取文本内容
        text = self.toPlainText()
        print(f"Sending: {text}")  # 这里可以替换为实际的发送逻辑
        self.clear()  # 清空输入框
from PyQt6.QtWidgets import QApplication, QTextEdit, QVBoxLayout, QWidget

class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('聊天气泡示例')
        self.setGeometry(100, 100, 400, 300)

        self.chat_display = QTextEdit(self)
        self.chat_display.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(self.chat_display)
        self.setLayout(layout)

        # 加载CSS文件
        self.load_stylesheet("styles.css")

        # 添加消息
        self.add_message("这是一条消息内容。")

    def load_stylesheet(self, filename):
        """加载CSS文件并将其应用到QTextEdit"""
        try:
            with open(filename, "r", encoding="utf-8") as file:
                stylesheet = file.read()
                # 将CSS样式插入到HTML的<style>标签中
                self.chat_display.document().setDefaultStyleSheet(stylesheet)
        except FileNotFoundError:
            print(f"CSS文件 {filename} 未找到")

    def add_message(self, message):
        """添加消息到聊天窗口"""
        html = f"""
<div class="sender">
  <div>
    <img src="https://statiwww.jyshare.com/images/mix/img_avatar.png">
  </div>
  <div>
    <div class="left_triangle"></div>
    <span> hello, man! </span>
  </div>
</div>
"""

        self.chat_display.insertHtml(html)

if __name__ == '__main__':
    app = QApplication([])
    window = ChatWindow()
    window.show()
    app.exec()
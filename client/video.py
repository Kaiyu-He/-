import sys
import cv2
import pyaudio
import numpy as np
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QApplication, QDialog
from PyQt6 import QtWidgets

from ui.video import Ui_Dialog

class VideoAudioDialog(QDialog, Ui_Dialog):
    def __init__(self):
        super().__init__()

        # 设置 UI
        self.setupUi(self)

        # 初始化 OpenCV 视频捕获
        self.cap = cv2.VideoCapture(0)  # 使用摄像头
        if not self.cap.isOpened():
            print("Error: Could not open video source.")
            sys.exit()

        # 初始化 PyAudio
        self.audio_from = pyaudio.PyAudio()
        self.stream_from = self.audio_from.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=44100,
            input=True,
            frames_per_buffer=1024,
            stream_callback=self.audio_callback
        )

        self.audio_to = pyaudio.PyAudio()
        self.stream_to = self.audio_to.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=44100,
            input=True,
            frames_per_buffer=1024,
            stream_callback=self.audio_callback2
        )

        # 定时器更新视频帧
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # 30ms 更新一次

        # 绑定按钮点击事件
        self.button.clicked.connect(self.close)

    def update_frame(self):
        """从摄像头捕获帧并显示"""
        ret, frame = self.cap.read()
        if ret:
            # 将 OpenCV 帧转换为 QImage
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)

            # 显示在 from_user 标签上
            self.from_user.setPixmap(QPixmap.fromImage(q_img))
            self.to_user.setPixmap(QPixmap.fromImage(q_img))


    def audio_callback(self, in_data, frame_count, time_info, status):
        """音频回调函数，处理音频数据"""
        # 这里可以添加音频处理逻辑
        print("Audio data received")
        return (in_data, pyaudio.paContinue)

    def audio_callback2(self, in_data, frame_count, time_info, status):
        """音频回调函数，处理音频数据"""
        # 这里可以添加音频处理逻辑
        print("Audio data received")
        return (in_data, pyaudio.paContinue)

    def closeEvent(self, event):
        """关闭窗口时释放资源"""
        self.cap.release()
        self.stream_from.stop_stream()
        self.stream_from.close()
        self.stream_to.stop_stream()
        self.stream_to.close()
        self.audio_from.terminate()
        self.audio_to.terminate()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = VideoAudioDialog()
    dialog.exec()  # 使用 exec() 以模态方式显示对话框
    sys.exit(app.exec())
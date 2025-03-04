import sys
import threading

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

        self.local = threading.Thread(target=self.send_thread)
        self.local.daemon = True
        self.local.start()

        self.receive_video = threading.Thread(target=self.receive_thread)
        self.receive_video.daemon = True
        self.receive_video.start()
        # 绑定按钮点击事件
        self.button.clicked.connect(self.close)

    def process_image_shape(self, frame, target_width, target_height):
        original_width, original_height = frame.shape[:2]

        # 计算缩放比例
        width_ratio = target_width / original_width
        height_ratio = target_height / original_height
        scale_ratio = min(width_ratio, height_ratio)

        # 计算缩放后的尺寸
        new_width = int(original_width * scale_ratio)
        new_height = int(original_height * scale_ratio)
        frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
        # 计算裁剪区域
        start_x = max(0, (new_width - target_width) // 2)
        start_y = max(0, (new_height - target_height) // 2)
        end_x = start_x + target_width
        end_y = start_y + target_height
        # 裁剪图片
        cropped_image = frame[start_y:end_y, start_x:end_x]

        return cropped_image

    def update_frame(self):
        """从摄像头捕获帧并显示"""
        ret, frame = self.cap.read()
        if ret:
            frame = self.process_image_shape(frame, 200, 300)
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
        return (in_data, pyaudio.paContinue)

    def audio_callback2(self, in_data, frame_count, time_info, status):
        """音频回调函数，处理音频数据"""
        # 这里可以添加音频处理逻辑
        return (in_data, pyaudio.paContinue)

    def send_thread(self):
        pass

    def receive_thread(self):
        # 实现接收视频流的逻辑
        pass
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
    dialog.exec()
    sys.exit(app.exec())

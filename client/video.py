import math
import socket
import struct
import sys
import threading
import time

import cv2
import numpy as np
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QApplication, QDialog

from ui.video import Ui_Dialog


class VideoAudioDialog(QDialog, Ui_Dialog):
    def __init__(self, ipv4, port, is_sender):
        super().__init__()
        self.ipv4 = ipv4
        self.port = port
        self.is_sender = is_sender
        self.connected = True
        self.MAX_DGRAM = 2 ** 30
        self.MAX_IMAGE_DGRAM = self.MAX_DGRAM - 64
        # 设置 UI
        self.setupUi(self)

        if is_sender:
            self.sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sender.bind((self.ipv4, self.port))
            self.sender.listen(5)
            self.s, addr = self.sender.accept()
            self.wait_accept = threading.Thread(target=self.wait)
            self.wait_accept.start()
        else:
            receiver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            receiver.connect((self.ipv4, self.port))
            print("connect")
            self.s = receiver
            self.button.setText("同意")
            self.button.clicked.connect(self.start)

        self.cap = cv2.VideoCapture(0)  # 使用摄像头
        if not self.cap.isOpened():
            print("Error: Could not open video source.")
            sys.exit()

    def wait(self):
        try:
            self.button.setText("结束")
            self.button.clicked.connect(self.close)
            signal = self.s.recv(1024).decode('utf-8')
            self.start()
        except:
            self.close()

    def start(self):
        self.s.send("start".encode('utf-8'))
        self.button.setText("结束")
        # self.button.clicked.disconnect(self.start)
        self.send_video = threading.Thread(target=self.send_thread)
        self.send_video.start()

        self.receive_video = threading.Thread(target=self.receive_thread)
        self.receive_video.start()

        self.button.clicked.connect(self.close)

    def process_image_shape(self, frame, target_width=200, target_height=300):
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

    def send_img(self, img):
        try:
            compress_img = cv2.imencode('.jpg', img)[1]
            dat = compress_img.tobytes()
            size = len(dat)
            count = math.ceil(size / self.MAX_IMAGE_DGRAM)
            array_pos_start = 0
            while count:
                array_pos_end = min(size, array_pos_start + self.MAX_IMAGE_DGRAM)
                self.s.send(struct.pack("B", count) +
                            dat[array_pos_start:array_pos_end])
                array_pos_start = array_pos_end
                count -= 1
        except ConnectionResetError as e:
            print(f"Connection reset by remote host: {e}")
            self.close()
        except Exception as e:
            print(f"Error sending image: {e}")
            self.close()

    def receive_img(self):
        try:
            dat = b''
            seg = self.s.recv(self.MAX_DGRAM)
            if struct.unpack("B", seg[0:1])[0] > 1:
                dat += seg[1:]
            else:
                dat += seg[1:]
                img = cv2.imdecode(np.frombuffer(dat, dtype=np.uint8), 1)
                if img is None:
                    print("Failed to decode image")
                    return None
                return img
        except ConnectionResetError as e:
            print(f"Connection reset by remote host: {e}")
            self.close()
            return None
        except Exception as e:
            print(f"Error receiving image: {e}")
            self.close()
            return None

    def send_thread(self):
        while self.connected:
            ret, frame = self.cap.read()
            self.send_img(frame)
            frame = self.process_image_shape(frame)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            self.from_user.setPixmap(QPixmap.fromImage(q_img))

    def receive_thread(self):
        while self.connected:
            frame = self.receive_img()
            if frame is None:
                continue
            frame = self.process_image_shape(frame)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)

            self.to_user.setPixmap(QPixmap.fromImage(q_img))

    def close(self):
        """关闭窗口时释放资源"""
        if self.connected is False:
            return
        self.connected = False
        time.sleep(1)
        print("close start")
        # 关闭网络连接
        try:
            if hasattr(self, 's'):
                self.s.close()
            if self.is_sender and hasattr(self, 'sender'):
                self.sender.close()
        except:
            print("close error")
        print("close socket")

        # 释放摄像头资源
        if self.cap:
            self.cap.release()
        print("close cap")
        # 关闭对话框
        super().close()


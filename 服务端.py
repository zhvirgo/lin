import socket
import sys
import threading
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QTextEdit
from PyQt5.QtCore import Qt


class ServerWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("服务器")
        self.resize(400, 300)

        self.ip_label = QLabel("IP 地址:", self)
        self.ip_label.move(20, 20)

        self.ip_edit = QLineEdit(self)
        self.ip_edit.move(100, 20)
        self.ip_edit.resize(180, 20)

        self.port_label = QLabel("端口:", self)
        self.port_label.move(20, 60)

        self.port_edit = QLineEdit(self)
        self.port_edit.move(100, 60)
        self.port_edit.resize(180, 20)

        self.start_button = QPushButton("启动服务器", self)
        self.start_button.move(20, 100)
        self.start_button.clicked.connect(self.start_server_thread)

        self.message_label = QLabel("消息:", self)
        self.message_label.move(20, 140)

        self.message_edit = QLineEdit(self)
        self.message_edit.move(100, 140)
        self.message_edit.resize(280, 20)

        self.send_to_client_button = QPushButton("发送给客户端", self)
        self.send_to_client_button.move(20, 180)
        self.send_to_client_button.clicked.connect(self.send_message_to_client)

        self.log_text = QTextEdit(self)
        self.log_text.move(20, 220)
        self.log_text.resize(360, 60)

        self.server_socket = None
        self.client_socket = None
        self.thread = None  # 用于存储线程对象

    def start_server_thread(self):
        if self.thread and self.thread.is_alive():  # 如果线程已存在且正在运行，不执行新的启动
            return
        self.thread = threading.Thread(target=self.start_server)
        self.thread.start()

    def start_server(self):
        ip = self.ip_edit.text()
        port = int(self.port_edit.text())

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.server_socket.bind((ip, port))
            self.server_socket.listen(1)
            self.log_text.append("服务器启动，等待连接...")

            self.client_socket, client_address = self.server_socket.accept()
            self.log_text.append(f"连接来自: {client_address}")

            while True:
                try:
                    data = self.client_socket.recv(1024).decode('utf-8')
                    if not data:
                        break
                    self.log_text.append(f"收到消息: {data}")
                except Exception as e:
                    self.log_text.append(f"接收消息出错: {e}")
        except Exception as e:
            self.log_text.append(f"服务器启动出错: {e}")
            self.server_socket.close()

    def send_message_to_client(self):
        message = self.message_edit.text()
        if self.client_socket:
            try:
                self.client_socket.send(message.encode('utf-8'))
                self.log_text.append(f"发送消息给客户端: {message}")
            except Exception as e:
                self.log_text.append(f"发送消息出错: {e}")
        else:
            self.log_text.append("尚未与客户端建立连接，无法发送消息")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    server_win = ServerWindow()
    server_win.show()
    sys.exit(app.exec_())
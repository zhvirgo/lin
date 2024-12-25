import socket
import sys
import threading
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QTextEdit
from PyQt5.QtCore import Qt


class ClientWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("客户端")
        self.resize(400, 300)

        self.server_ip_label = QLabel("服务器 IP 地址:", self)
        self.server_ip_label.move(20, 20)

        self.server_ip_edit = QLineEdit(self)
        self.server_ip_edit.move(150, 20)
        self.server_ip_edit.resize(180, 20)

        self.server_port_label = QLabel("服务器端口:", self)
        self.server_port_label.move(20, 60)

        self.server_port_edit = QLineEdit(self)
        self.server_port_edit.move(150, 60)
        self.server_port_edit.resize(180, 20)

        self.login_button = QPushButton("登录", self)
        self.login_button.move(20, 100)
        self.login_button.clicked.connect(self.start_connection_thread)

        self.message_label = QLabel("消息:", self)
        self.message_label.move(20, 140)

        self.message_edit = QLineEdit(self)
        self.message_edit.move(100, 140)
        self.message_edit.resize(280, 20)

        self.send_button = QPushButton("发送", self)
        self.send_button.move(20, 180)
        self.send_button.clicked.connect(self.send_message)

        self.log_text = QTextEdit(self)
        self.log_text.move(20, 220)
        self.log_text.resize(360, 60)

        self.client_socket = None
        self.connected = False
        self.receive_thread = None  # 新增接收线程对象

    def start_connection_thread(self):
        if self.connected:
            self.log_text.append("已连接到服务器，无需重复连接")
            return
        thread = threading.Thread(target=self.connect_to_server)
        thread.start()

    def connect_to_server(self):
        server_ip = self.server_ip_edit.text()
        server_port = int(self.server_port_edit.text())

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((server_ip, server_port))
            self.connected = True
            self.log_text.append("连接成功")
            self.start_receive_thread()  # 连接成功后启动接收线程
        except socket.gaierror as e:
            self.log_text.append(f"地址解析错误: {e}")
        except socket.timeout:
            self.log_text.append("连接超时，请检查服务器是否运行以及网络连接")
        except socket.error as e:
            self.log_text.append(f"连接错误: {e}")
        except Exception as e:
            self.log_text.append(f"未知错误: {e}")

    def start_receive_thread(self):
        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.daemon = True  # 设置为守护线程，主线程退出时自动结束
        self.receive_thread.start()

    def receive_messages(self):
        while self.connected:
            try:
                data = self.client_socket.recv(1024).decode('utf-8')
                if data:
                    self.log_text.append(f"收到消息: {data}")
            except socket.timeout:
                continue
            except socket.error as e:
                self.log_text.append(f"接收消息时出错: {e}，连接可能已断开")
                self.connected = False
                break
            except Exception as e:
                self.log_text.append(f"未知错误: {e}，连接可能已断开")
                self.connected = False
                break

    def send_message(self):
        if not self.connected:
            self.log_text.append("尚未连接到服务器，无法发送消息")
            return
        message = self.message_edit.text()
        try:
            self.client_socket.send(message.encode('utf-8'))
            self.log_text.append(f"发送消息: {message}")
            self.message_edit.clear()
            self.log_text.ensureCursorVisible()
        except socket.timeout:
            self.log_text.append("发送消息超时，请检查网络连接")
        except socket.error as e:
            self.log_text.append(f"发送消息时出错: {e}")
        except Exception as e:
            self.log_text.append(f"未知错误: {e}")

    def closeEvent(self, event):
        if self.connected and self.client_socket:
            self.connected = False
            self.client_socket.close()
            if self.receive_thread and self.receive_thread.is_alive():
                self.receive_thread.join()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    client_win = ClientWindow()
    client_win.show()
    sys.exit(app.exec_())
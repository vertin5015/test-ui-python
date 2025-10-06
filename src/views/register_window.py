from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QHBoxLayout, QSizePolicy

class RegisterWindow(QWidget):
    def __init__(self, controller, switch_to_login):
        super().__init__()
        self.controller = controller
        self.switch_to_login = switch_to_login
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("注册")
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        layout.addWidget(QLabel("邮箱:"))
        self.email_input = QLineEdit()
        layout.addWidget(self.email_input)

        code_layout = QHBoxLayout()
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("输入注册码")
        send_btn = QPushButton("发送注册码")
        send_btn.clicked.connect(self.on_send_code)
        code_layout.addWidget(self.code_input)
        code_layout.addWidget(send_btn)
        layout.addLayout(code_layout)

        layout.addWidget(QLabel("设置密码:"))
        self.pw1 = QLineEdit(); self.pw1.setEchoMode(QLineEdit.Password)
        self.pw2 = QLineEdit(); self.pw2.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.pw1); layout.addWidget(self.pw2)

        confirm_btn = QPushButton("确认注册")
        confirm_btn.clicked.connect(self.on_confirm_register)
        layout.addWidget(confirm_btn)

        back_btn = QPushButton("返回登录")
        back_btn.clicked.connect(self.switch_to_login)
        layout.addWidget(back_btn)

        layout.addStretch(1)
        self.setLayout(layout)
        self.setMinimumSize(400, 360)

    def on_send_code(self):
        email = self.email_input.text().strip()
        ok, msg = self.controller.send_registration_code(email)
        if ok:
            QMessageBox.information(self, "发送", msg)
        else:
            QMessageBox.warning(self, "错误", msg or "发送失败")

    def on_confirm_register(self):
        email = self.email_input.text().strip()
        code = self.code_input.text().strip()
        p1 = self.pw1.text().strip(); p2 = self.pw2.text().strip()
        if p1 != p2:
            QMessageBox.warning(self, "错误", "两次密码不一致")
            return
        ok, msg = self.controller.register_with_code(email, code, p1)
        if ok:
            QMessageBox.information(self, "成功", "注册成功，请登录")
            self.switch_to_login()
        else:
            QMessageBox.warning(self, "失败", msg or "注册失败")

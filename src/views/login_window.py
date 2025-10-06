from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QSizePolicy

class LoginWindow(QWidget):
    def __init__(self, controller, switch_to_register, switch_to_level_select):
        super().__init__()
        self.controller = controller
        self.switch_to_register = switch_to_register
        self.switch_to_level_select = switch_to_level_select
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("登录")
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        email_label = QLabel("邮箱:")
        layout.addWidget(email_label)

        self.email_input = QLineEdit()
        layout.addWidget(self.email_input)

        pw_label = QLabel("密码:")
        layout.addWidget(pw_label)

        self.pw_input = QLineEdit()
        self.pw_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.pw_input)

        login_btn = QPushButton("登录")
        login_btn.clicked.connect(self.on_login_clicked)
        layout.addWidget(login_btn)

        reg_btn = QPushButton("注册")
        reg_btn.clicked.connect(self.switch_to_register)
        layout.addWidget(reg_btn)

        layout.addStretch(1)
        self.setLayout(layout)
        self.setMinimumSize(360, 280)

    def on_login_clicked(self):
        email = self.email_input.text().strip()
        pw = self.pw_input.text().strip()
        ok, msg = self.controller.login(email, pw)
        if ok:
            QMessageBox.information(self, "成功", "登录成功")
            self.switch_to_level_select()
        else:
            QMessageBox.warning(self, "失败", msg or "登录失败")

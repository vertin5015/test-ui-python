from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QHBoxLayout, QSizePolicy

class ChangePasswordDialog(QDialog):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("修改密码")
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        old_label = QLabel("原密码:")
        layout.addWidget(old_label)
        self.old_input = QLineEdit()
        self.old_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.old_input)

        new_label = QLabel("新密码:")
        layout.addWidget(new_label)
        self.new_input = QLineEdit()
        self.new_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.new_input)

        confirm_label = QLabel("确认新密码:")
        layout.addWidget(confirm_label)
        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.confirm_input)

        btns = QHBoxLayout()
        ok_btn = QPushButton("确认修改")
        cancel_btn = QPushButton("取消")
        ok_btn.clicked.connect(self.on_confirm)
        cancel_btn.clicked.connect(self.reject)
        btns.addWidget(ok_btn)
        btns.addWidget(cancel_btn)
        layout.addLayout(btns)

        self.setLayout(layout)
        self.setMinimumSize(380, 260)

    def on_confirm(self):
        old_pw = self.old_input.text().strip()
        new_pw = self.new_input.text().strip()
        confirm_pw = self.confirm_input.text().strip()

        if not old_pw or not new_pw or not confirm_pw:
            QMessageBox.warning(self, "错误", "请完整填写所有字段")
            return

        if new_pw != confirm_pw:
            QMessageBox.warning(self, "错误", "两次新密码不一致")
            return

        ok, msg = self.controller.change_password(old_pw, new_pw)
        if ok:
            QMessageBox.information(self, "成功", "密码修改成功")
            self.accept()
        else:
            QMessageBox.warning(self, "失败", msg or "修改失败")

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QRadioButton, QSpinBox, QButtonGroup, QMessageBox
from .change_password_dialog import ChangePasswordDialog

class LevelSelectWindow(QWidget):
    def __init__(self, controller, start_quiz_callback, back_to_login):
        super().__init__()
        self.controller = controller
        self.start_quiz_callback = start_quiz_callback
        self.back_to_login = back_to_login
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("选择学段与题量")
        layout = QVBoxLayout()
        layout.addWidget(QLabel("选择学段:"))
        self.group = QButtonGroup()
        self.r1 = QRadioButton("小学")
        self.r2 = QRadioButton("初中")
        self.r3 = QRadioButton("高中")
        self.r1.setChecked(True)
        for rb in [self.r1, self.r2, self.r3]:
            self.group.addButton(rb)
            layout.addWidget(rb)

        layout.addWidget(QLabel("题目数量:"))
        self.spin = QSpinBox()
        self.spin.setRange(1, 100)
        self.spin.setValue(10)
        layout.addWidget(self.spin)

        start_btn = QPushButton("开始做题")
        start_btn.clicked.connect(self.on_start)
        layout.addWidget(start_btn)

        change_pw_btn = QPushButton("修改密码")
        change_pw_btn.clicked.connect(self.on_change_password)
        layout.addWidget(change_pw_btn)

        logout_btn = QPushButton("退出登录")
        logout_btn.clicked.connect(self.back_to_login)
        layout.addWidget(logout_btn)

        layout.addStretch(1)
        self.setLayout(layout)
        self.setMinimumSize(380, 320)

    def on_start(self):
        level_map = {self.r1: "elementary", self.r2: "middle", self.r3: "high"}
        for rb, lvl in level_map.items():
            if rb.isChecked():
                level = lvl
                break
        n = self.spin.value()
        self.controller.start_quiz(level, n)
        self.start_quiz_callback()

    def on_change_password(self):
        dlg = ChangePasswordDialog(self.controller, self)
        dlg.exec()

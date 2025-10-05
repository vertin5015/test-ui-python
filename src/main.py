# main.py
import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QHBoxLayout, QRadioButton, QButtonGroup, QSpinBox, QScrollArea, QSizePolicy, QDialog
from controllers.app_controller import AppController
import config

class LoginWindow(QWidget):
    def __init__(self, controller: AppController, switch_to_register, switch_to_level_select):
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
        email_label.setWordWrap(True)
        layout.addWidget(email_label)

        self.email_input = QLineEdit()
        self.email_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(self.email_input)

        pw_label = QLabel("密码:")
        pw_label.setWordWrap(True)
        layout.addWidget(pw_label)

        self.pw_input = QLineEdit()
        self.pw_input.setEchoMode(QLineEdit.Password)
        self.pw_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
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

class RegisterWindow(QWidget):
    def __init__(self, controller: AppController, switch_to_login):
        super().__init__()
        self.controller = controller
        self.switch_to_login = switch_to_login
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("注册")
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        email_label = QLabel("邮箱:")
        email_label.setWordWrap(True)
        layout.addWidget(email_label)
        self.email_input = QLineEdit()
        self.email_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(self.email_input)
        code_layout = QHBoxLayout()
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("输入注册码")
        self.code_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        send_btn = QPushButton("发送注册码")
        send_btn.clicked.connect(self.on_send_code)
        code_layout.addWidget(self.code_input)
        code_layout.addWidget(send_btn)
        layout.addLayout(code_layout)
        pw_set_label = QLabel("设置密码:")
        pw_set_label.setWordWrap(True)
        layout.addWidget(pw_set_label)
        self.pw1 = QLineEdit(); self.pw1.setEchoMode(QLineEdit.Password)
        self.pw2 = QLineEdit(); self.pw2.setEchoMode(QLineEdit.Password)
        self.pw1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.pw2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
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

class LevelSelectWindow(QWidget):
    def __init__(self, controller: AppController, start_quiz_callback, back_to_login):
        super().__init__()
        self.controller = controller
        self.start_quiz_callback = start_quiz_callback
        self.back_to_login = back_to_login
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("选择学段与题量")
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        level_label = QLabel("选择学段:")
        level_label.setWordWrap(True)
        layout.addWidget(level_label)
        self.group = QButtonGroup()
        self.r1 = QRadioButton("小学")
        self.r2 = QRadioButton("初中")
        self.r3 = QRadioButton("高中")
        self.r1.setChecked(True)
        self.group.addButton(self.r1); self.group.addButton(self.r2); self.group.addButton(self.r3)
        layout.addWidget(self.r1); layout.addWidget(self.r2); layout.addWidget(self.r3)
        qnum_label = QLabel("题目数量:")
        qnum_label.setWordWrap(True)
        layout.addWidget(qnum_label)
        self.spin = QSpinBox()
        self.spin.setMinimum(1)
        self.spin.setMaximum(100)
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
                level = lvl; break
        n = self.spin.value()
        self.controller.start_quiz(level, n)
        self.start_quiz_callback()

    def on_change_password(self):
        dlg = ChangePasswordDialog(self.controller, self)
        dlg.exec()

class ChangePasswordDialog(QDialog):
    def __init__(self, controller: AppController, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("修改密码")
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        old_label = QLabel("原密码:")
        old_label.setWordWrap(True)
        layout.addWidget(old_label)
        self.old_input = QLineEdit()
        self.old_input.setEchoMode(QLineEdit.Password)
        self.old_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(self.old_input)

        new_label = QLabel("新密码:")
        new_label.setWordWrap(True)
        layout.addWidget(new_label)
        self.new_input = QLineEdit()
        self.new_input.setEchoMode(QLineEdit.Password)
        self.new_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(self.new_input)

        confirm_label = QLabel("确认新密码:")
        confirm_label.setWordWrap(True)
        layout.addWidget(confirm_label)
        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.Password)
        self.confirm_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
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

class QuizWindow(QWidget):
    def __init__(self, controller: AppController, show_result_callback):
        super().__init__()
        self.controller = controller
        self.show_result_callback = show_result_callback
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("答题")
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(16, 16, 16, 16)
        self.layout.setSpacing(12)

        self.stem_label = QLabel("")
        self.stem_label.setWordWrap(True)
        self.stem_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.layout.addWidget(self.stem_label)

        # 使用滚动区域容纳选项，保证小窗口下可滚动
        self.options_scroll = QScrollArea()
        self.options_scroll.setWidgetResizable(True)
        options_container = QWidget()
        self.options_layout = QVBoxLayout(options_container)
        self.options_layout.setContentsMargins(0, 0, 0, 0)
        self.options_layout.setSpacing(8)

        self.option_buttons = []
        self.option_group = QButtonGroup()
        for i in range(4):
            rb = QRadioButton()
            rb.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            self.option_group.addButton(rb, i)
            self.options_layout.addWidget(rb)
            self.option_buttons.append(rb)
        self.options_layout.addStretch(1)
        self.options_scroll.setWidget(options_container)
        self.layout.addWidget(self.options_scroll)

        btn_layout = QHBoxLayout()
        self.next_btn = QPushButton("下一题")
        self.next_btn.clicked.connect(self.on_next)
        self.submit_btn = QPushButton("交卷")
        self.submit_btn.clicked.connect(self.on_submit)
        btn_layout.addWidget(self.next_btn); btn_layout.addWidget(self.submit_btn)
        self.layout.addLayout(btn_layout)
        self.layout.addStretch(1)
        self.setLayout(self.layout)
        self.setMinimumSize(500, 380)
        # self.load_question(0)

    def load_question(self, index):
        q = self.controller.current_paper[index]
        self.stem_label.setText(f"第 {index+1} 题: {q['stem']}")
        for i, opt in enumerate(q['options']):
            self.option_buttons[i].setText(opt)
            self.option_buttons[i].setChecked(False)
        # 如果用户已选过，设置显示
        sel = self.controller.current_answers[index]
        if sel is not None and sel >= 0:
            b = self.option_group.button(sel)
            if b:
                b.setChecked(True)

    def on_next(self):
        idx = self.controller.current_index
        sel = self.option_group.checkedId()
        if sel is not None and sel != -1:
            self.controller.submit_answer(idx, sel)
        # 下一题
        if self.controller.next_question():
            self.load_question(self.controller.current_index)
        else:
            QMessageBox.information(self, "提示", "已经是最后一题")

    def on_submit(self):
        idx = self.controller.current_index
        sel = self.option_group.checkedId()
        if sel is not None and sel != -1:
            self.controller.submit_answer(idx, sel)
        result = self.controller.finish_quiz_and_score()
        self.show_result_callback(result)

class ResultWindow(QWidget):
    def __init__(self, controller: AppController, back_to_level_select):
        super().__init__()
        self.controller = controller
        self.back_to_level_select = back_to_level_select
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("成绩")
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(16, 16, 16, 16)
        self.layout.setSpacing(12)
        self.label = QLabel("")
        self.label.setWordWrap(True)
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.layout.addWidget(self.label)
        btn_layout = QHBoxLayout()
        retry = QPushButton("继续做题")
        retry.clicked.connect(self.on_retry)
        exit_btn = QPushButton("退出程序")
        exit_btn.clicked.connect(self.on_exit)
        btn_layout.addWidget(retry); btn_layout.addWidget(exit_btn)
        self.layout.addLayout(btn_layout)
        self.layout.addStretch(1)
        self.setLayout(self.layout)
        self.setMinimumSize(420, 300)

    def show_result(self, result: dict):
        s = f"共 {result['total']} 题，答对 {result['correct']}。成绩：{result['score_pct']} %"
        self.label.setText(s)

    def on_retry(self):
        self.back_to_level_select()

    def on_exit(self):
        QApplication.quit()

class AppWindow:
    def __init__(self):
        self.qtapp = QApplication(sys.argv)
        self.controller = AppController(self.qtapp)
        # windows
        self.login = LoginWindow(self.controller, self.show_register, self.show_level_select)
        self.register = RegisterWindow(self.controller, self.show_login)
        self.level_select = LevelSelectWindow(self.controller, self.start_quiz, self.show_login)
        self.quiz = QuizWindow(self.controller, self.show_result)
        self.result = ResultWindow(self.controller, self.show_level_select)

    def show_login(self):
        self.hide_all()
        self.login.show()

    def show_register(self):
        self.hide_all()
        self.register.show()

    def show_level_select(self):
        self.hide_all()
        self.level_select.show()

    def start_quiz(self):
        self.hide_all()
        self.quiz = QuizWindow(self.controller, self.show_result)
        # 这里保证 start_quiz 已经调用过 controller.start_quiz
        self.quiz.load_question(0)
        self.quiz.show()

    def show_result(self, result):
        self.hide_all()
        self.result.show_result(result)
        self.result.show()

    def hide_all(self):
        for w in [self.login, self.register, self.level_select, self.quiz, self.result]:
            try:
                w.hide()
            except:
                pass

    def run(self):
        self.show_login()
        sys.exit(self.qtapp.exec())

if __name__ == "__main__":
    appwin = AppWindow()
    appwin.run()

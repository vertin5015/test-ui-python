# main.py
import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QHBoxLayout, QRadioButton, QButtonGroup, QSpinBox
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
        layout.addWidget(QLabel("邮箱:"))
        self.email_input = QLineEdit()
        layout.addWidget(self.email_input)
        layout.addWidget(QLabel("密码:"))
        self.pw_input = QLineEdit()
        self.pw_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.pw_input)
        login_btn = QPushButton("登录")
        login_btn.clicked.connect(self.on_login_clicked)
        layout.addWidget(login_btn)
        reg_btn = QPushButton("注册")
        reg_btn.clicked.connect(self.switch_to_register)
        layout.addWidget(reg_btn)
        self.setLayout(layout)

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
        self.setLayout(layout)

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
        layout.addWidget(QLabel("选择学段:"))
        self.group = QButtonGroup()
        self.r1 = QRadioButton("小学")
        self.r2 = QRadioButton("初中")
        self.r3 = QRadioButton("高中")
        self.r1.setChecked(True)
        self.group.addButton(self.r1); self.group.addButton(self.r2); self.group.addButton(self.r3)
        layout.addWidget(self.r1); layout.addWidget(self.r2); layout.addWidget(self.r3)
        layout.addWidget(QLabel("题目数量:"))
        self.spin = QSpinBox()
        self.spin.setMinimum(1)
        self.spin.setMaximum(100)
        self.spin.setValue(10)
        layout.addWidget(self.spin)
        start_btn = QPushButton("开始做题")
        start_btn.clicked.connect(self.on_start)
        layout.addWidget(start_btn)
        logout_btn = QPushButton("退出登录")
        logout_btn.clicked.connect(self.back_to_login)
        layout.addWidget(logout_btn)
        self.setLayout(layout)

    def on_start(self):
        level_map = {self.r1: "elementary", self.r2: "middle", self.r3: "high"}
        for rb, lvl in level_map.items():
            if rb.isChecked():
                level = lvl; break
        n = self.spin.value()
        self.controller.start_quiz(level, n)
        self.start_quiz_callback()

class QuizWindow(QWidget):
    def __init__(self, controller: AppController, show_result_callback):
        super().__init__()
        self.controller = controller
        self.show_result_callback = show_result_callback
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("答题")
        self.layout = QVBoxLayout()
        self.stem_label = QLabel("")
        self.layout.addWidget(self.stem_label)
        self.option_buttons = []
        self.option_group = QButtonGroup()
        for i in range(4):
            rb = QRadioButton()
            self.option_group.addButton(rb, i)
            self.layout.addWidget(rb)
            self.option_buttons.append(rb)
        btn_layout = QHBoxLayout()
        self.next_btn = QPushButton("下一题")
        self.next_btn.clicked.connect(self.on_next)
        self.submit_btn = QPushButton("交卷")
        self.submit_btn.clicked.connect(self.on_submit)
        btn_layout.addWidget(self.next_btn); btn_layout.addWidget(self.submit_btn)
        self.layout.addLayout(btn_layout)
        self.setLayout(self.layout)
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
        self.label = QLabel("")
        self.layout.addWidget(self.label)
        btn_layout = QHBoxLayout()
        retry = QPushButton("继续做题")
        retry.clicked.connect(self.on_retry)
        exit_btn = QPushButton("退出程序")
        exit_btn.clicked.connect(self.on_exit)
        btn_layout.addWidget(retry); btn_layout.addWidget(exit_btn)
        self.layout.addLayout(btn_layout)
        self.setLayout(self.layout)

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

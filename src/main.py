# main.py
import sys
from PySide6.QtWidgets import QApplication
from controllers.app_controller import AppController

from views.login_window import LoginWindow
from views.register_window import RegisterWindow
from views.level_select_window import LevelSelectWindow
from views.quiz_window import QuizWindow
from views.result_window import ResultWindow


class AppWindow:
    def __init__(self):
        self.qtapp = QApplication(sys.argv)
        self.controller = AppController(self.qtapp)

        # 初始化各个窗口
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

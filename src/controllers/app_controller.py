# controllers/app_controller.py
from models.user_manager import UserManager
from models.question_bank import QuestionBank

class AppController:
    def __init__(self, app, users_file=None, questions_dir=None):
        self.app = app
        self.user_manager = UserManager(users_file) if users_file else UserManager()
        self.question_bank = QuestionBank(questions_dir) if questions_dir else QuestionBank()
        self.current_user = None
        self.current_paper = []
        self.current_answers = []  # 存放用户选择的索引（-1 表示未答）
        self.current_index = 0

    # 注册相关
    def send_registration_code(self, email: str) -> (bool, str):
        from utils.validators import is_valid_email
        if not is_valid_email(email):
            return False, "邮箱格式不正确"
        ok = self.user_manager.send_registration_code(email)
        if ok:
            return True, "注册码已发送（若收不到邮件，请检查垃圾箱或联系管理员）"
        return False, "邮件发送失败"

    def register_with_code(self, email: str, code: str, password: str) -> (bool, str):
        return self.user_manager.register_with_code(email, code, password)

    def login(self, email: str, password: str) -> (bool, str):
        ok = self.user_manager.verify_login(email, password)
        if ok:
            self.current_user = email
            return True, ""
        return False, "账号或密码错误"

    def change_password(self, old_pw: str, new_pw: str) -> (bool, str):
        if not self.current_user:
            return False, "未登录"
        return self.user_manager.change_password(self.current_user, old_pw, new_pw)

    # 出题与答题
    def start_quiz(self, level: str, n_questions: int):
        self.current_paper = self.question_bank.generate_paper(level, n_questions)
        self.current_index = 0
        self.current_answers = [-1] * len(self.current_paper)

    def get_current_question(self):
        if not self.current_paper:
            return None
        return self.current_paper[self.current_index]

    def submit_answer(self, index: int, selected_option: int):
        if index < 0 or index >= len(self.current_answers):
            return
        self.current_answers[index] = selected_option

    def next_question(self):
        if self.current_index < len(self.current_paper) - 1:
            self.current_index += 1
            return True
        return False

    def prev_question(self):
        if self.current_index > 0:
            self.current_index -= 1
            return True
        return False

    def finish_quiz_and_score(self) -> dict:
        total = len(self.current_paper)
        correct = 0
        for i, q in enumerate(self.current_paper):
            if self.current_answers[i] == q["answer"]:
                correct += 1
        score_pct = int((correct / total) * 100) if total > 0 else 0
        result = {
            "total": total,
            "correct": correct,
            "score_pct": score_pct
        }
        return result

import os
import random
import uuid
import math
import re
from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Set

import config
from utils.helpers import read_json, write_json

DEFAULT_LEVELS = ["elementary", "middle", "high"]


class AbstractQuestionGenerator(ABC):
    """抽象题目生成器：子类需要实现 create_stem_and_answer，返回 (stem, answer)。"""

    @abstractmethod
    def create_stem_and_answer(self) -> Tuple[str, float]:
        raise NotImplementedError


class ElementaryGenerator(AbstractQuestionGenerator):
    """小学题目生成器：生成简单的加减乘除整式算术题（结果为整数）。"""

    def __init__(self, min_start: int = 10, max_start: int = 50, max_operand: int = 20):
        self.min_start = min_start
        self.max_start = max_start
        self.max_operand = max_operand
        self.operators = ["+", "-", "*", "/"]

    def create_stem_and_answer(self) -> Tuple[str, int]:
        num_operands = random.randint(2, 4)
        running_total = random.randint(self.min_start, self.max_start)
        parts = [str(running_total)]

        for _ in range(num_operands - 1):
            op = random.choice(self.operators)
            operand = random.randint(1, self.max_operand)

            # 修正不合适的操作（避免负数或非整除）
            if op == "-" and operand > running_total:
                op = "+"
            if op == "/" and (operand == 0 or running_total % operand != 0):
                op = "*"

            parts.append(f"{op} {operand}")

            if op == "+":
                running_total += operand
            elif op == "-":
                running_total -= operand
            elif op == "*":
                running_total *= operand
            elif op == "/":
                running_total //= operand

        stem = " ".join(parts) + " = ?"
        return stem, running_total


class MiddleGenerator(AbstractQuestionGenerator):
    """初中题目生成器：支持平方、开方与基本四则混合运算（结果可能为浮点数）。"""

    def __init__(self, max_operand: int = 20):
        self.max_operand = max_operand

    def create_stem_and_answer(self) -> Tuple[str, float]:
        num_operands = random.randint(2, 4)
        operands = [str(random.randint(1, self.max_operand)) for _ in range(num_operands)]
        special_index = random.randint(0, num_operands - 1)

        # 40% 生成开方，否则生成平方
        if random.random() < 0.4:
            val = random.choice([4, 9, 16, 25, 36, 49, 64, 81, 100])
            operands[special_index] = f"sqrt({val})"
        else:
            val = random.randint(2, 12)
            operands[special_index] = f"{val}^2"

        basic_operators = ["+", "-", "*"]
        parts = [operands[0]]
        for i in range(1, num_operands):
            op = random.choice(basic_operators)
            parts.append(f"{op} {operands[i]}")

        stem = " ".join(parts) + " = ?"

        # 评估表达式：把 sqrt/ ^ 替换为 math 表达式
        eval_str = stem.replace("?", "").replace("=", "")
        eval_str = eval_str.replace("sqrt", "math.sqrt").replace("^", "**")
        try:
            answer = eval(eval_str, {"math": math})
        except Exception:
            # 若 eval 出错则退回到一个简单的整数题
            return ElementaryGenerator().create_stem_and_answer()

        return stem, answer


class HighGenerator(AbstractQuestionGenerator):
    """高中题目生成器：支持三角函数（以角度给出）与基本运算。"""

    def __init__(self, max_operand: int = 20):
        self.max_operand = max_operand
        self.trig_functions = ["sin", "cos", "tan"]
        self.allowed_angles = [0, 30, 45, 60, 90]

    def create_stem_and_answer(self) -> Tuple[str, float]:
        num_operands = random.randint(2, 4)
        operands = [str(random.randint(1, self.max_operand)) for _ in range(num_operands)]
        special_index = random.randint(0, num_operands - 1)

        func = random.choice(self.trig_functions)
        angle = random.choice(self.allowed_angles)
        # tan(90°) 无意义，避免出现
        if func == "tan" and angle == 90:
            angle = random.choice([0, 30, 45, 60])

        operands[special_index] = f"{func}({angle}°)"

        basic_operators = ["+", "-", "*"]
        parts = [operands[0]]
        for i in range(1, num_operands):
            op = random.choice(basic_operators)
            parts.append(f"{op} {operands[i]}")

        stem = " ".join(parts) + " = ?"

        # 替换 trig(...) 为 math.xxx(math.radians(angle))
        def trig_replacer(match: re.Match) -> str:
            func_name, angle_val = match.groups()
            return f"math.{func_name}(math.radians({angle_val}))"

        eval_str = stem.replace("?", "").replace("=", "").replace("°", "")
        eval_str = re.sub(r"(sin|cos|tan)\((\d+)\)", trig_replacer, eval_str)

        try:
            answer = eval(eval_str, {"math": math})
        except Exception:
            # 回退到初中题目以保证稳定性
            return MiddleGenerator().create_stem_and_answer()

        return stem, answer


def _build_options_and_index(answer: float) -> Tuple[List[str], int]:
    """根据答案生成四个选项（字符串形式），并返回正确选项的索引。"""
    # 如果答案是非整数的浮点数，则保留两位小数
    if isinstance(answer, float) and abs(answer - round(answer)) > 1e-9:
        correct_str = f"{answer:.2f}"
        options = {correct_str}
        while len(options) < 4:
            delta = random.uniform(-5, 5)
            options.add(f"{(answer + delta):.2f}")
    else:
        int_ans = int(round(answer))
        correct_str = str(int_ans)
        options = {correct_str}
        while len(options) < 4:
            delta = random.randint(-8, 8)
            if delta == 0:
                continue
            options.add(str(int_ans + delta))

    options_list = list(options)
    random.shuffle(options_list)
    answer_index = options_list.index(correct_str)
    return options_list, answer_index


class QuestionBank:
    """题库管理：使用具体的题目生成器创建并维护题库，接口与原实现兼容。"""

    def __init__(self, questions_dir: str = config.QUESTIONS_DIR):
        self.questions_dir = questions_dir
        self.raw: Dict[str, List[Dict]] = {lvl: [] for lvl in DEFAULT_LEVELS}
        self.existing_stems: Dict[str, Set[str]] = {lvl: set() for lvl in DEFAULT_LEVELS}

        # 生成器映射（便于未来注入或替换）
        self.generators: Dict[str, AbstractQuestionGenerator] = {
            "elementary": ElementaryGenerator(),
            "middle": MiddleGenerator(),
            "high": HighGenerator(),
        }

        self.load_question_files()

    def load_question_files(self):
        """加载题库文件；若不存在则生成初始题目并保存。"""
        if not os.path.exists(self.questions_dir):
            os.makedirs(self.questions_dir, exist_ok=True)

        for lvl in DEFAULT_LEVELS:
            path = os.path.join(self.questions_dir, f"{lvl}.json")
            data = read_json(path)
            if data:
                self.raw[lvl] = data
            else:
                # 初始生成少量题目填充文件
                self.raw[lvl] = self._generate_and_add_new_questions(lvl, 10, save=False)
                self._save_questions_to_file(lvl)

            self.existing_stems[lvl] = {q["stem"] for q in self.raw[lvl]}
        print("Question bank loaded.")

    def _save_questions_to_file(self, level: str):
        path = os.path.join(self.questions_dir, f"{level}.json")
        write_json(path, self.raw[level])

    def _create_new_question(self, level: str) -> Dict:
        """使用对应级别的生成器创建一个不重复的新题目（含选项与答案索引）。"""
        if level not in self.generators:
            raise ValueError(f"Level must be one of: {', '.join(DEFAULT_LEVELS)}")

        # 尝试生成一个不重复的题干
        max_attempts = 50
        for _ in range(max_attempts):
            stem, answer = self.generators[level].create_stem_and_answer()
            if stem not in self.existing_stems[level]:
                self.existing_stems[level].add(stem)
                options_list, answer_index = _build_options_and_index(answer)
                return {
                    "id": str(uuid.uuid4()),
                    "stem": stem,
                    "options": options_list,
                    "answer": answer_index,
                }
        # 若多次失败，作为降级策略返回一个简单题目
        stem, answer = ElementaryGenerator().create_stem_and_answer()
        options_list, answer_index = _build_options_and_index(answer)
        return {"id": str(uuid.uuid4()), "stem": stem, "options": options_list, "answer": answer_index}

    def _generate_and_add_new_questions(self, level: str, n: int, save: bool = True) -> List[Dict]:
        new_questions = [self._create_new_question(level) for _ in range(n)]
        self.raw[level].extend(new_questions)
        if save:
            self._save_questions_to_file(level)
        return new_questions

    def generate_paper(self, level: str, n_questions: int) -> List[Dict]:
        """生成试卷；接口与旧版本兼容，题库不足时自动补足并保存。"""
        if level not in DEFAULT_LEVELS:
            raise ValueError(f"Level must be one of: {', '.join(DEFAULT_LEVELS)}")

        pool = self.raw[level]
        if len(pool) < n_questions:
            num_to_generate = n_questions - len(pool)
            print(f"Question pool for '{level}' is insufficient. Generating {num_to_generate} new questions...")
            self._generate_and_add_new_questions(level, num_to_generate)
            print("New questions have been generated and saved.")

        return random.sample(self.raw[level], n_questions)

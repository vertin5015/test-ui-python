import random
import math
import re
from typing import Tuple
from .abstract_generator import AbstractQuestionGenerator
from .middle_generator import MiddleGenerator


class HighGenerator(AbstractQuestionGenerator):
    """高中题目生成器：支持三角函数与基本运算。"""

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
        if func == "tan" and angle == 90:
            angle = random.choice([0, 30, 45, 60])

        operands[special_index] = f"{func}({angle}°)"
        parts = [operands[0]]
        for i in range(1, num_operands):
            parts.append(f"{random.choice(['+', '-', '*'])} {operands[i]}")

        stem = " ".join(parts) + " = ?"

        def trig_replacer(m: re.Match) -> str:
            f, a = m.groups()
            return f"math.{f}(math.radians({a}))"

        eval_str = re.sub(r"(sin|cos|tan)\((\d+)\)", trig_replacer, stem.replace("?", "").replace("=", "").replace("°", ""))
        try:
            answer = eval(eval_str, {"math": math})
        except Exception:
            return MiddleGenerator().create_stem_and_answer()

        return stem, answer

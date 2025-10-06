import random
import math
from typing import Tuple
from .abstract_generator import AbstractQuestionGenerator
from .elementary_generator import ElementaryGenerator


class MiddleGenerator(AbstractQuestionGenerator):
    """初中题目生成器：支持平方、开方与基本四则混合运算。"""

    def __init__(self, max_operand: int = 20):
        self.max_operand = max_operand

    def create_stem_and_answer(self) -> Tuple[str, float]:
        num_operands = random.randint(2, 4)
        operands = [str(random.randint(1, self.max_operand)) for _ in range(num_operands)]
        special_index = random.randint(0, num_operands - 1)

        # 40% 生成 sqrt，否则平方
        if random.random() < 0.4:
            val = random.choice([4, 9, 16, 25, 36, 49, 64, 81, 100])
            operands[special_index] = f"sqrt({val})"
        else:
            val = random.randint(2, 12)
            operands[special_index] = f"{val}^2"

        basic_ops = ["+", "-", "*"]
        parts = [operands[0]]
        for i in range(1, num_operands):
            op = random.choice(basic_ops)
            parts.append(f"{op} {operands[i]}")

        stem = " ".join(parts) + " = ?"
        eval_str = stem.replace("?", "").replace("=", "")
        eval_str = eval_str.replace("sqrt", "math.sqrt").replace("^", "**")

        try:
            answer = eval(eval_str, {"math": math})
        except Exception:
            return ElementaryGenerator().create_stem_and_answer()

        return stem, answer

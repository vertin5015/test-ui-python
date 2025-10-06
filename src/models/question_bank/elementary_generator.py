import random
from typing import Tuple
from .abstract_generator import AbstractQuestionGenerator


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

            # 修正非法操作
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

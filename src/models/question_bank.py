# models/question_bank.py
import os
import json
import random
import uuid
from typing import List, Dict
import config
from utils.helpers import read_json

DEFAULT_LEVELS = ["elementary", "middle", "high"]

class QuestionBank:
    def __init__(self, questions_dir: str = config.QUESTIONS_DIR):
        self.questions_dir = questions_dir
        self.raw = {lvl: [] for lvl in DEFAULT_LEVELS}
        self.load_question_files()

    def load_question_files(self):
        # 尝试加载 data/questions/*.json
        if not os.path.exists(self.questions_dir):
            os.makedirs(self.questions_dir, exist_ok=True)
        for lvl in DEFAULT_LEVELS:
            path = os.path.join(self.questions_dir, f"{lvl}.json")
            data = read_json(path)
            if data:
                self.raw[lvl] = data
            else:
                # 若文件不存在或为空，生成一些默认题目模板
                self.raw[lvl] = self._generate_default_questions(lvl, 50)

    def _generate_default_questions(self, level: str, n:int=50) -> List[Dict]:
        """
        生成简单的选择题作为占位：主要用于演示。
        elementary: 加减乘除
        middle: 一元一次、解方程/代数基础
        high: 函数/几何/三角（简单题）
        """
        qs = []
        for _ in range(n):
            qid = str(uuid.uuid4())
            if level == "elementary":
                a = random.randint(1, 20)
                b = random.randint(1, 20)
                op = random.choice(["+", "-", "*"])
                if op == "+":
                    ans = a + b
                elif op == "-":
                    ans = a - b
                else:
                    ans = a * b
                stem = f"{a} {op} {b} = ?"
                correct = str(ans)
                # 生成三个干扰项
                opts = {correct}
                while len(opts) < 4:
                    delta = random.randint(-5, 5)
                    opts.add(str(ans + delta))
                opts = list(opts)
                random.shuffle(opts)
                answer_index = opts.index(correct)
                qs.append({"id": qid, "stem": stem, "options": opts, "answer": answer_index})
            elif level == "middle":
                # 解决简单的线性方程： ax + b = c
                a = random.randint(1, 9)
                x = random.randint(-10, 10)
                b = random.randint(-10, 10)
                c = a * x + b
                stem = f"解方程：{a}x + {b} = {c}，x = ?"
                correct = str(x)
                opts = {correct}
                while len(opts) < 4:
                    opts.add(str(x + random.randint(-3, 3)))
                opts = list(opts)
                random.shuffle(opts)
                answer_index = opts.index(correct)
                qs.append({"id": qid, "stem": stem, "options": opts, "answer": answer_index})
            else:  # high
                # 计算直角三角形斜边（简单）
                a = random.randint(3, 12)
                b = random.randint(3, 12)
                import math
                c = int((a*a + b*b)**0.5)
                stem = f"直角三角形两直角边为 {a} 和 {b}，斜边约等于？（整数近似）"
                correct = str(c)
                opts = {correct}
                while len(opts) < 4:
                    opts.add(str(c + random.randint(-4, 4)))
                opts = list(opts)
                random.shuffle(opts)
                answer_index = opts.index(correct)
                qs.append({"id": qid, "stem": stem, "options": opts, "answer": answer_index})
        return qs

    def generate_paper(self, level: str, n_questions: int) -> List[Dict]:
        if level not in DEFAULT_LEVELS:
            raise ValueError("level must be one of: " + ",".join(DEFAULT_LEVELS))
        pool = self.raw[level].copy()
        # 如果题库不足，重用生成器 / 抛出错误。这里尽量允许重用不同 ID 的随机题（防止重复）
        if len(pool) >= n_questions:
            selected = random.sample(pool, n_questions)
            return selected
        else:
            # 如果题目不够，从默认生成器补足（生成新的题目 ID 保证与已有题不同）
            additional = self._generate_default_questions(level, n_questions - len(pool))
            pool.extend(additional)
            selected = random.sample(pool, n_questions)
            # 保证同一卷中没有重复题（by id），实现已经保证
            return selected

    def add_custom_question(self, level: str, question: Dict):
        self.raw[level].append(question)
        # 可选：写回文件（这里简单追加，生产需注意文件写入冲突）
        path = os.path.join(self.questions_dir, f"{level}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.raw[level], f, ensure_ascii=False, indent=2)

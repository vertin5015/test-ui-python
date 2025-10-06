import os
import uuid
import random
from typing import List, Dict, Set

import config
from utils.helpers import read_json, write_json
from .elementary_generator import ElementaryGenerator
from .middle_generator import MiddleGenerator
from .high_generator import HighGenerator
from .utils import build_options_and_index

DEFAULT_LEVELS = ["elementary", "middle", "high"]


class QuestionBank:
    """题库管理器"""

    def __init__(self, questions_dir: str = config.QUESTIONS_DIR):
        self.questions_dir = questions_dir
        self.raw: Dict[str, List[Dict]] = {lvl: [] for lvl in DEFAULT_LEVELS}
        self.existing_stems: Dict[str, Set[str]] = {lvl: set() for lvl in DEFAULT_LEVELS}

        self.generators = {
            "elementary": ElementaryGenerator(),
            "middle": MiddleGenerator(),
            "high": HighGenerator(),
        }

        self.load_question_files()

    def load_question_files(self):
        """加载题目文件，确保历史题目查重功能正常"""
        if not os.path.exists(self.questions_dir):
            os.makedirs(self.questions_dir, exist_ok=True)
        for lvl in DEFAULT_LEVELS:
            path = os.path.join(self.questions_dir, f"{lvl}.json")
            data = read_json(path)
            if data:
                self.raw[lvl] = data
                print(f"已加载{lvl}级别历史题目{len(data)}道")
            else:
                self.raw[lvl] = self._generate_and_add_new_questions(lvl, 10, save=False)
                self._save(lvl)
                print(f"创建新的{lvl}级别题库，包含{len(self.raw[lvl])}道题目")
            # 更新历史题目记录，用于查重
            self.existing_stems[lvl] = {q["stem"] for q in self.raw[lvl]}
            print(f"{lvl}级别历史题目查重记录已更新，共{len(self.existing_stems[lvl])}道不重复题目")

    def _save(self, level: str):
        """保存指定级别的题目到JSON文件"""
        path = os.path.join(self.questions_dir, f"{level}.json")
        write_json(path, self.raw[level])
        print(f"已保存{level}级别题目到文件：{path}")
    
    def save_all_questions(self):
        """保存所有级别的题目到对应的JSON文件"""
        for level in DEFAULT_LEVELS:
            self._save(level)
        print("所有级别题目已保存完成")

    def _create_question(self, level: str) -> Dict:
        """创建新题目，确保不与历史题目重复"""
        gen = self.generators[level]
        max_attempts = 100  # 增加尝试次数
        
        for _ in range(max_attempts):
            stem, ans = gen.create_stem_and_answer()
            if stem not in self.existing_stems[level]:
                self.existing_stems[level].add(stem)
                opts, idx = build_options_and_index(ans)
                return {"id": str(uuid.uuid4()), "stem": stem, "options": opts, "answer": idx}
        
        # 如果尝试多次后仍然重复，使用小学题目生成器作为备选
        print(f"警告：{level}级别题目生成器尝试{max_attempts}次后仍有重复，使用小学题目生成器")
        stem, ans = self.generators["elementary"].create_stem_and_answer()
        opts, idx = build_options_and_index(ans)
        return {"id": str(uuid.uuid4()), "stem": stem, "options": opts, "answer": idx}

    def _generate_and_add_new_questions(self, level: str, n: int, save=True) -> List[Dict]:
        """生成新题目并添加到题库，确保保存到JSON文件"""
        new = [self._create_question(level) for _ in range(n)]
        self.raw[level].extend(new)
        if save:
            self._save(level)
            print(f"已生成{n}道{level}级别新题目并保存到JSON文件")
        return new

    def generate_paper(self, level: str, n: int) -> List[Dict]:
        """生成全新试卷，每次使用题目生成器创建新题目，确保不重复"""
        print(f"开始生成{level}级别试卷，共{n}道题目")
        
        # 生成全新的题目
        new_questions = []
        used_stems = set()  # 用于当次生成查重
        
        for i in range(n):
            attempts = 0
            max_attempts = 100
            
            while attempts < max_attempts:
                # 使用题目生成器创建新题目
                gen = self.generators[level]
                stem, ans = gen.create_stem_and_answer()
                
                # 检查是否与历史题目重复
                if stem not in self.existing_stems[level] and stem not in used_stems:
                    # 创建题目对象
                    opts, idx = build_options_and_index(ans)
                    question = {
                        "id": str(uuid.uuid4()),
                        "stem": stem,
                        "options": opts,
                        "answer": idx
                    }
                    new_questions.append(question)
                    used_stems.add(stem)
                    self.existing_stems[level].add(stem)
                    print(f"  生成题目{i+1}: {stem}")
                    break
                attempts += 1
            
            if attempts >= max_attempts:
                print(f"  警告：题目{i+1}生成失败，尝试{max_attempts}次后仍有重复")
                # 使用备选方案
                gen = self.generators["elementary"]
                stem, ans = gen.create_stem_and_answer()
                opts, idx = build_options_and_index(ans)
                question = {
                    "id": str(uuid.uuid4()),
                    "stem": stem,
                    "options": opts,
                    "answer": idx
                }
                new_questions.append(question)
                used_stems.add(stem)
                self.existing_stems[level].add(stem)
                print(f"  使用备选题目{i+1}: {stem}")
        
        # 将新生成的题目添加到题库并保存
        self.raw[level].extend(new_questions)
        self._save(level)
        print(f"已生成{n}道全新{level}级别题目并保存到JSON文件")
        
        return new_questions
    
    def refresh_historical_questions(self, level: str = None):
        """刷新历史题目记录，重新加载题目文件"""
        if level:
            # 刷新指定级别
            path = os.path.join(self.questions_dir, f"{level}.json")
            data = read_json(path)
            if data:
                self.raw[level] = data
                self.existing_stems[level] = {q["stem"] for q in self.raw[level]}
                print(f"已刷新{level}级别历史题目记录，共{len(self.existing_stems[level])}道不重复题目")
        else:
            # 刷新所有级别
            self.load_question_files()

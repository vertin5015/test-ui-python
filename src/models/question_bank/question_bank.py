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
        if not os.path.exists(self.questions_dir):
            os.makedirs(self.questions_dir, exist_ok=True)
        for lvl in DEFAULT_LEVELS:
            path = os.path.join(self.questions_dir, f"{lvl}.json")
            data = read_json(path)
            if data:
                self.raw[lvl] = data
            else:
                self.raw[lvl] = self._generate_and_add_new_questions(lvl, 10, save=False)
                self._save(lvl)
            self.existing_stems[lvl] = {q["stem"] for q in self.raw[lvl]}

    def _save(self, level: str):
        write_json(os.path.join(self.questions_dir, f"{level}.json"), self.raw[level])

    def _create_question(self, level: str) -> Dict:
        gen = self.generators[level]
        for _ in range(50):
            stem, ans = gen.create_stem_and_answer()
            if stem not in self.existing_stems[level]:
                self.existing_stems[level].add(stem)
                opts, idx = build_options_and_index(ans)
                return {"id": str(uuid.uuid4()), "stem": stem, "options": opts, "answer": idx}
        stem, ans = self.generators["elementary"].create_stem_and_answer()
        opts, idx = build_options_and_index(ans)
        return {"id": str(uuid.uuid4()), "stem": stem, "options": opts, "answer": idx}

    def _generate_and_add_new_questions(self, level: str, n: int, save=True) -> List[Dict]:
        new = [self._create_question(level) for _ in range(n)]
        self.raw[level].extend(new)
        if save:
            self._save(level)
        return new

    def generate_paper(self, level: str, n: int) -> List[Dict]:
        if len(self.raw[level]) < n:
            self._generate_and_add_new_questions(level, n - len(self.raw[level]))
        return random.sample(self.raw[level], n)

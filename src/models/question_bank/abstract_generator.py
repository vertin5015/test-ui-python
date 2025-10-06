from abc import ABC, abstractmethod
from typing import Tuple


class AbstractQuestionGenerator(ABC):
    """抽象题目生成器：子类必须实现 create_stem_and_answer。"""

    @abstractmethod
    def create_stem_and_answer(self) -> Tuple[str, float]:
        raise NotImplementedError

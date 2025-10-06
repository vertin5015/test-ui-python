import random
from typing import List, Tuple


def build_options_and_index(answer: float) -> Tuple[List[str], int]:
    """根据答案生成四个选项和正确答案索引。"""
    if isinstance(answer, float) and abs(answer - round(answer)) > 1e-9:
        correct = f"{answer:.2f}"
        options = {correct}
        while len(options) < 4:
            delta = random.uniform(-5, 5)
            options.add(f"{(answer + delta):.2f}")
    else:
        correct = str(int(round(answer)))
        options = {correct}
        while len(options) < 4:
            delta = random.randint(-8, 8)
            if delta != 0:
                options.add(str(int(correct) + delta))

    opts = list(options)
    random.shuffle(opts)
    return opts, opts.index(correct)

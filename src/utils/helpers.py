# utils/helpers.py
import json
import os
import random
import string
from typing import Any

def read_json(path: str) -> Any:
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def write_json(path: str, data: Any) -> None:
    parent = os.path.dirname(path)
    if not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def random_code(length:int=6) -> str:
    return ''.join(random.choices(string.digits, k=length))

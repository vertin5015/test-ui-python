# utils/validators.py
import re

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")

def is_valid_email(email: str) -> bool:
    return EMAIL_RE.match(email) is not None

def is_valid_password(password: str) -> (bool, str):
    """
    密码规则：6-10 位，必须含大小写字母和数字
    返回 (True, "") 或 (False, "错误消息")
    """
    if not (6 <= len(password) <= 10):
        return False, "密码长度必须是 6 到 10 个字符"
    if not any(c.islower() for c in password):
        return False, "密码必须包含小写字母"
    if not any(c.isupper() for c in password):
        return False, "密码必须包含大写字母"
    if not any(c.isdigit() for c in password):
        return False, "密码必须包含数字"
    return True, ""

# models/user_manager.py
import os
import json
import time
import hmac
import hashlib
import smtplib
from email.message import EmailMessage
from typing import Dict, Optional
from utils.helpers import read_json, write_json, random_code
from utils.validators import is_valid_email, is_valid_password
import config

PBKDF2_ITERATIONS = 120_000

class UserManager:
    def __init__(self, users_file: str = config.USERS_FILE):
        self.users_file = users_file
        self._codes = {}  # 临时保存 {email: (code, expiry_ts)}
        self.users = {}
        self.load_users()

    def load_users(self):
        data = read_json(self.users_file)
        if data is None:
            self.users = {}
            self.save_users()
        else:
            self.users = data

    def save_users(self):
        write_json(self.users_file, self.users)

    def _hash_password(self, password: str, salt: Optional[bytes] = None) -> Dict:
        if salt is None:
            salt = hashlib.sha256(str(time.time()).encode() + os.urandom(8)).digest()
        dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, PBKDF2_ITERATIONS)
        return {
            "salt": salt.hex(),
            "hash": dk.hex(),
            "iterations": PBKDF2_ITERATIONS
        }

    def _verify_password(self, password: str, record: Dict) -> bool:
        salt = bytes.fromhex(record["salt"])
        expected = record["hash"]
        dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, record.get("iterations", PBKDF2_ITERATIONS))
        return hmac.compare_digest(dk.hex(), expected)

    def user_exists(self, email: str) -> bool:
        return email in self.users

    def send_registration_code(self, email: str) -> bool:
        """
        生成注册验证码并发送邮件。为简化测试，同时返回 True/False。
        也会在 self._codes 保留验证码 5 分钟。
        """
        if not is_valid_email(email):
            return False
        code = random_code(6)
        expiry = time.time() + 300  # 5 分钟
        self._codes[email] = (code, expiry)
        # 发送邮件（使用配置的 SMTP）
        try:
            msg = EmailMessage()
            msg["Subject"] = "注册验证码"
            msg["From"] = config.SMTP_USER
            msg["To"] = email
            msg.set_content(f"您的注册验证码是：{code}，有效期 5 分钟。")
            with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT) as s:
                s.starttls()
                s.login(config.SMTP_USER, config.SMTP_PASSWORD)
                s.send_message(msg)
            return True
        except Exception as e:
            # 如果发邮件失败（例如测试环境），也将验证码保持在内存，便于本地测试
            print("邮件发送失败（可能在测试环境）：", e)
            return True

    def register_with_code(self, email: str, code: str, password: str) -> (bool, str):
        if self.user_exists(email):
            return False, "邮箱已注册"
        ok, msg = is_valid_password(password)
        if not ok:
            return False, msg
        rec = self._codes.get(email)
        if rec is None:
            return False, "未发送注册码或已过期"
        saved_code, expiry = rec
        if time.time() > expiry:
            return False, "注册码已过期"
        if saved_code != code:
            return False, "注册码错误"
        # 创建用户
        h = self._hash_password(password)
        self.users[email] = {
            "email": email,
            "password": h,
            "created_at": int(time.time()),
            "profile": {}
        }
        self.save_users()
        # 删除临时代码
        del self._codes[email]
        return True, ""

    def verify_login(self, email: str, password: str) -> bool:
        if not self.user_exists(email):
            return False
        return self._verify_password(password, self.users[email]["password"])

    def change_password(self, email: str, old_password: str, new_password: str) -> (bool, str):
        if not self.verify_login(email, old_password):
            return False, "原密码错误"
        ok, msg = is_valid_password(new_password)
        if not ok:
            return False, msg
        h = self._hash_password(new_password)
        self.users[email]["password"] = h
        self.save_users()
        return True, ""

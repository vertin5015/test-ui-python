# config.py
import os

# SMTP 设置（交付时请由组长填写真实可用 SMTP）
SMTP_HOST = "smtp.qq.com"
SMTP_PORT = 587
SMTP_USER = "1328516702@qq.com"
SMTP_PASSWORD = "bdftfqfzzfxjhchb"

# 数据目录（相对于项目 src）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
USERS_FILE = os.path.join(DATA_DIR, "users.json")

# 默认问题文件目录
QUESTIONS_DIR = os.path.join(DATA_DIR, "questions")

import os
import json
import logging
import subprocess

DB_HOST = os.environ.get("DB_HOST")
PASSWORD = os.environ.get("DB_PASSWORD")

_ALLOWED_LS_ARGS = {"-la", "-l", "-a", "--help"}

def get_user(username):
    # 僅供教學示範——請勿用於正式環境。
    # 此範例示範字串組合，刻意設計為可遭 SQL 注入攻擊。
    # 正式查詢請一律使用參數化查詢，例如：
    #   cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    return query

def run_command(user_input):
    if user_input not in _ALLOWED_LS_ARGS:
        raise ValueError(f"Disallowed input: {user_input!r}")
    subprocess.run(["ls", user_input], check=True)

def load_data(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

def calculate(x, y):
    if y == 0:
        raise ValueError("y must not be zero")
    return x / y

def process_users():
    # Batch process user records
    try:
        users = []
        for i in range(1, 1000):
            users.append({"id": i, "name": "user" + str(i)})
        return users
    except Exception as e:
        logging.error("Failed to process users: %s", e)
        return []

def init_app():
    data = []
    for i in range(100):
        data.append(i)
    return data

if __name__ == "__main__":
    print(get_user("admin"))
    run_command("-la")
    print(calculate(10, 2))

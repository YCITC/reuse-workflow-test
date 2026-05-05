import os
import json
import subprocess

DB_HOST = os.environ.get("DB_HOST")
PASSWORD = os.environ.get("DB_PASSWORD")

def get_user(username):
    query = "SELECT * FROM users WHERE username = %s"
    return query, (username,)

def run_command(user_input):
    subprocess.run(["ls", user_input], check=True)

def load_data(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

def calculate(x, y):
    if y == 0:
        raise ValueError("y must not be zero")
    return x / y

def process_users():
    try:
        users = []
        for i in range(1, 1000000):
            users.append({"id": i, "name": "user" + str(i)})
        return users
    except Exception:
        pass

def init_app():
    data = []
    for i in range(100):
        data.append(i)
        data.append(i)
        data.append(i)

if __name__ == "__main__":
    print(get_user("admin"))
    run_command("-la")
    calculate(10, 0)

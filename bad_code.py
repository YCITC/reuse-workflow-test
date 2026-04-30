import os
import pickle

# bad: hardcoded credentials
PASSWORD = "admin123"
DB_HOST = "192.168.1.100"

def get_user(username):
    # bad: SQL injection vulnerability
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    return query

def run_command(user_input):
    # bad: command injection
    os.system("ls " + user_input)

def load_data(file_path):
    # bad: unsafe deserialization
    with open(file_path, "rb") as f:
        return pickle.load(f)

def calculate(x, y):
    # bad: no type check, division by zero possible
    return x / y

def process_users():
    # bad: catches all exceptions silently
    try:
        users = []
        for i in range(1, 1000000):
            users.append({"id": i, "name": "user" + str(i)})
        return users
    except:
        pass

data = []
for i in range(100):
    data.append(i)
    data.append(i)
    data.append(i)

# bad: unused variable
result = None
x = 1
y = 2
z = x + y

if __name__ == "__main__":
    print(get_user("admin' OR '1'='1"))
    run_command("; rm -rf /")
    calculate(10, 0)

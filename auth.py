import json
import hashlib
import os

USER_DB = "users.json"


def load_users():
    if not os.path.exists(USER_DB):
        return {"users": {}}
    with open(USER_DB, "r") as file:
        return json.load(file)


def save_users(data):
    with open(USER_DB, "w") as file:
        json.dump(data, file, indent=4)


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def signup(username, password):
    data = load_users()

    if username in data["users"]:
        return False, "Username already exists"

    data["users"][username] = {
        "password": hash_password(password),
        "tasks": [],
        "memory": []
    }

    save_users(data)
    return True, "Signup successful"


def login(username, password):
    data = load_users()

    if username not in data["users"]:
        return False, "User not found"

    stored_password = data["users"][username]["password"]

    if stored_password == hash_password(password):
        return True, "Login successful"

    return False, "Incorrect password"
import json
import hashlib
import os
import re
from datetime import datetime

USERS_FILE = 'data/users.json'
TASKS_FILE = 'data/tasks.json'

def load_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return {}

def save_data(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2, default=str)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_current_user():
    if os.path.exists('data/session.json'):
        with open('data/session.json', 'r') as f:
            session = json.load(f)
            return session.get('current_email')
    return None

def set_current_user(email):
    with open('data/session.json', 'w') as f:
        json.dump({'current_email': email}, f)

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    if len(password) < 10:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[0-9]', password):
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    return True

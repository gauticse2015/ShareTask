from src.utils import load_data, save_data, hash_password, USERS_FILE, set_current_user, get_current_user, validate_email, validate_password
from datetime import datetime

def register_user(email, password, name):
    if not validate_email(email):
        return False, "Invalid email format"
    if not validate_password(password):
        return False, "Password must be at least 10 chars, include uppercase, number, and special char"
    users = load_data(USERS_FILE)
    if email in users:
        return False, "User already exists"
    users[email] = {
        'name': name,
        'password_hash': hash_password(password),
        'registered_at': str(datetime.now())
    }
    save_data(USERS_FILE, users)
    return True, "User registered successfully"

def login_user(email, password):
    users = load_data(USERS_FILE)
    if email in users and users[email]['password_hash'] == hash_password(password):
        current = get_current_user()
        if current and current != email:
            msg = f"Logging out {current} and logging in {email}"
        else:
            msg = "Login successful"
        set_current_user(email)
        return True, msg
    return False, "Invalid credentials"

def get_user_by_email(email):
    users = load_data(USERS_FILE)
    return users.get(email)

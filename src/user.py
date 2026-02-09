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
        'registered_at': str(datetime.now()),
        'notifications': []
    }
    save_data(USERS_FILE, users)
    return True, "User registered successfully"

def login_user(email, password, set_session=True):
    users = load_data(USERS_FILE)
    if email in users and users[email]['password_hash'] == hash_password(password):
        if set_session:
            current = get_current_user()
            if current and current != email:
                msg = f"Logging out {current} and logging in {email}"
            else:
                msg = "Login successful"
            set_current_user(email)
        else:
            msg = "Login successful"
        return True, msg
    return False, "Invalid credentials"

def get_user_by_email(email):
    users = load_data(USERS_FILE)
    return users.get(email)

def add_notification(user_email, message, notif_type='info', task_id=None):
    users = load_data(USERS_FILE)
    if user_email not in users:
        return False, "User not found"
    if 'notifications' not in users[user_email]:
        users[user_email]['notifications'] = []
    notif = {
        'id': str(datetime.now()),
        'message': message,
        'type': notif_type,
        'timestamp': str(datetime.now()),
        'read': False,
        'task_id': task_id
    }
    users[user_email]['notifications'].append(notif)
    users[user_email]['notifications'] = users[user_email]['notifications'][-20:]
    save_data(USERS_FILE, users)
    return True, "Notification added"

def get_notifications(user_email):
    users = load_data(USERS_FILE)
    user = users.get(user_email, {})
    notifs = user.get('notifications', [])
    notifs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    return notifs

def mark_notification_read(user_email, notif_id):
    users = load_data(USERS_FILE)
    if user_email not in users or 'notifications' not in users[user_email]:
        return False, "No notifications"
    for n in users[user_email]['notifications']:
        if n.get('id') == notif_id:
            n['read'] = True
            save_data(USERS_FILE, users)
            return True, "Marked read"
    return False, "Notification not found"

from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash, send_from_directory
import uuid
import os
from functools import wraps
from src.user import register_user, login_user, get_user_by_email
from src.task import create_task, share_task, update_task_status, list_tasks, revoke_share, add_comment, generate_report, start_live_task, stop_live_task, checkin_live_task, leave_live_task, get_live_status, delete_task
from src.utils import USERS_FILE, TASKS_FILE, load_data

app = Flask(__name__)
app.secret_key = 'secret_key_for_session'

tokens = {}

def generate_token():
    return str(uuid.uuid4())

def token_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        if not token or token not in tokens.values():
            return jsonify({'error': 'Unauthorized'}), 401
        user_email = next((email for email, t in tokens.items() if t == token), None)
        return f(user_email, *args, **kwargs)
    return wrapper

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_email' not in session:
            flash('Please login first')
            return redirect(url_for('ui_login'))
        return f(*args, **kwargs)
    return wrapper

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json()
    if not data or 'email' not in data or 'password' not in data or 'name' not in data:
        return jsonify({'error': 'Missing fields'}), 400
    success, msg = register_user(data['email'], data['password'], data['name'])
    if success:
        return jsonify({'message': msg}), 201
    return jsonify({'error': msg}), 400

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Missing fields'}), 400
    success, msg = login_user(data['email'], data['password'], set_session=False)
    if success:
        token = generate_token()
        tokens[data['email']] = token
        return jsonify({'message': msg, 'token': token}), 200
    return jsonify({'error': msg}), 401

@app.route('/api/tasks', methods=['POST'])
@token_required
def api_create_task(user_email):
    data = request.get_json()
    if not data or 'title' not in data or 'description' not in data or 'frequency' not in data or 'due_date' not in data:
        return jsonify({'error': 'Missing fields'}), 400
    task_type = data.get('type', 'normal')
    success, msg = create_task(data['title'], data['description'], data['frequency'], data['due_date'], task_type, user_email)
    if success:
        return jsonify({'message': msg}), 201
    return jsonify({'error': msg}), 400

@app.route('/api/tasks', methods=['GET'])
@token_required
def api_list_tasks(user_email):
    success, msg, tasks = list_tasks(False, user_email)
    if success:
        return jsonify({'message': msg, 'tasks': tasks}), 200
    return jsonify({'error': msg}), 400

@app.route('/api/tasks/<task_id>', methods=['DELETE'])
@token_required
def api_delete_task(user_email, task_id):
    success, msg = delete_task(task_id, user_email)
    if success:
        return jsonify({'message': msg}), 200
    return jsonify({'error': msg}), 400

@app.route('/api/tasks/<task_id>/share', methods=['POST'])
@token_required
def api_share_task(user_email, task_id):
    data = request.get_json()
    if not data or 'email' not in data:
        return jsonify({'error': 'Missing email'}), 400
    success, msg = share_task(task_id, data['email'], user_email)
    if success:
        return jsonify({'message': msg}), 200
    return jsonify({'error': msg}), 400

@app.route('/api/tasks/<task_id>/revoke', methods=['POST'])
@token_required
def api_revoke_share(user_email, task_id):
    data = request.get_json()
    if not data or 'email' not in data:
        return jsonify({'error': 'Missing email'}), 400
    success, msg = revoke_share(task_id, data['email'], user_email)
    if success:
        return jsonify({'message': msg}), 200
    return jsonify({'error': msg}), 400

@app.route('/api/tasks/<task_id>/comment', methods=['POST'])
@token_required
def api_add_comment(user_email, task_id):
    data = request.get_json()
    if not data or 'comment' not in data:
        return jsonify({'error': 'Missing comment'}), 400
    tags = data.get('tags', [])
    success, msg = add_comment(task_id, data['comment'], tags, user_email)
    if success:
        return jsonify({'message': msg}), 200
    return jsonify({'error': msg}), 400

@app.route('/api/tasks/<task_id>/status', methods=['PUT'])
@token_required
def api_update_status(user_email, task_id):
    data = request.get_json()
    if not data or 'status' not in data:
        return jsonify({'error': 'Missing status'}), 400
    success, msg = update_task_status(task_id, data['status'], user_email)
    if success:
        return jsonify({'message': msg}), 200
    return jsonify({'error': msg}), 400

@app.route('/api/tasks/<task_id>/start-live', methods=['POST'])
@token_required
def api_start_live(user_email, task_id):
    data = request.get_json() or {}
    duration = data.get('duration')
    success, msg = start_live_task(task_id, duration, user_email)
    if success:
        return jsonify({'message': msg}), 200
    return jsonify({'error': msg}), 400

@app.route('/api/tasks/<task_id>/stop-live', methods=['POST'])
@token_required
def api_stop_live(user_email, task_id):
    success, msg = stop_live_task(task_id, user_email)
    if success:
        return jsonify({'message': msg}), 200
    return jsonify({'error': msg}), 400

@app.route('/api/tasks/<task_id>/checkin-live', methods=['POST'])
@token_required
def api_checkin_live(user_email, task_id):
    success, msg = checkin_live_task(task_id, user_email)
    if success:
        return jsonify({'message': msg}), 200
    return jsonify({'error': msg}), 400

@app.route('/api/tasks/<task_id>/live-status', methods=['GET'])
@token_required
def api_live_status(user_email, task_id):
    success, msg, status = get_live_status(task_id, user_email)
    if success:
        return jsonify({'message': msg, 'status': status}), 200
    return jsonify({'error': msg}), 400

@app.route('/api/report', methods=['POST'])
@token_required
def api_generate_report(user_email):
    success, report = generate_report(user_email)
    if success:
        return jsonify({'message': 'Report generated', 'report': report}), 200
    return jsonify({'error': report}), 400

# UI routes for frontend screens
@app.route('/')
def ui_home_redirect():
    if 'user_email' in session:
        return redirect(url_for('ui_home'))
    return redirect(url_for('ui_login'))

@app.route('/signup', methods=['GET', 'POST'])
def ui_signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        success, msg = register_user(email, password, name)
        if success:
            flash(msg)
            return redirect(url_for('ui_login'))
        flash(msg)
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def ui_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        success, msg = login_user(email, password, set_session=False)
        if success:
            session['user_email'] = email
            token = generate_token()
            tokens[email] = token
            flash(msg)
            return redirect(url_for('ui_home'))
        flash(msg)
    return render_template('login.html')

@app.route('/logout')
def ui_logout():
    session.pop('user_email', None)
    flash('Logged out')
    return redirect(url_for('ui_login'))

@app.route('/home')
@login_required
def ui_home():
    user_email = session.get('user_email')
    success, msg, tasks_list = list_tasks(False, user_email)
    tasks = tasks_list if success else []
    return render_template('home.html', tasks=tasks, user_email=user_email)

@app.route('/generate-report', methods=['POST'])
@login_required
def ui_generate_report():
    user_email = session.get('user_email')
    success, report = generate_report(user_email)
    return render_template('report.html', report=report)

@app.route('/download-report', methods=['POST'])
@login_required
def download_report():
    file_type = request.form.get('format', 'txt')
    filename = f'task_report.{file_type}'
    return send_from_directory('data', filename, as_attachment=True)

@app.route('/profile')
@login_required
def ui_profile():
    user_email = session.get('user_email')
    user_data = get_user_by_email(user_email)
    user_name = user_data.get('name', 'N/A') if user_data else 'N/A'
    return render_template('profile.html', user_email=user_email, user_name=user_name)

@app.route('/create-task', methods=['GET', 'POST'])
@login_required
def ui_create_task():
    if request.method == 'POST':
        user_email = session.get('user_email')
        title = request.form.get('title')
        description = request.form.get('description')
        frequency = request.form.get('frequency')
        due_date = request.form.get('due_date')
        task_type = request.form.get('type', 'normal')
        start_time = request.form.get('start_time') if task_type == 'live' else None
        duration = int(request.form.get('duration')) if task_type == 'live' and request.form.get('duration') else None
        success, msg = create_task(title, description, frequency, due_date, task_type, user_email, start_time, duration)
        if success:
            flash(msg)
            return redirect(url_for('ui_home'))
        flash(msg)
    return render_template('create_task.html')

@app.route('/delete-task/<task_id>', methods=['POST'])
@login_required
def ui_delete_task(task_id):
    user_email = session.get('user_email')
    success, msg = delete_task(task_id, user_email)
    if success:
        flash(msg)
    else:
        flash(msg)
    return redirect(url_for('ui_home'))

@app.route('/task/<task_id>')
@login_required
def ui_task_details(task_id):
    user_email = session.get('user_email')
    success, msg, tasks_list = list_tasks(False, user_email)
    task = None
    if success:
        for tid, t in tasks_list:
            if tid == task_id:
                task = t
                break
    if not task:
        flash('Task not found')
        return redirect(url_for('ui_home'))
    return render_template('task_details.html', task=task, task_id=task_id, user_email=user_email)

@app.route('/task/<task_id>/share', methods=['POST'])
@login_required
def ui_share_task(task_id):
    user_email = session.get('user_email')
    share_email = request.form.get('share_email')
    if share_email:
        success, msg = share_task(task_id, share_email, user_email)
        flash(msg)
    return redirect(url_for('ui_task_details', task_id=task_id))

@app.route('/task/<task_id>/comment', methods=['POST'])
@login_required
def ui_add_comment(task_id):
    user_email = session.get('user_email')
    comment = request.form.get('comment')
    tags = request.form.get('tags', '').split(',')
    if comment:
        success, msg = add_comment(task_id, comment, tags, user_email)
        flash(msg)
    return redirect(url_for('ui_task_details', task_id=task_id))

@app.route('/task/<task_id>/start-live', methods=['POST'])
@login_required
def ui_start_live_task(task_id):
    user_email = session.get('user_email')
    duration = request.form.get('duration')
    duration = int(duration) if duration else None
    success, msg = start_live_task(task_id, duration, user_email)
    flash(msg)
    return redirect(url_for('ui_task_details', task_id=task_id))

@app.route('/task/<task_id>/join-live', methods=['POST'])
@login_required
def ui_join_live(task_id):
    user_email = session.get('user_email')
    success, msg = checkin_live_task(task_id, user_email)
    flash(msg)
    return redirect(url_for('ui_task_details', task_id=task_id))

@app.route('/task/<task_id>/leave-live', methods=['POST'])
@login_required
def ui_leave_live(task_id):
    user_email = session.get('user_email')
    success, msg = leave_live_task(task_id, user_email)
    flash(msg)
    return redirect(url_for('ui_task_details', task_id=task_id))

@app.route('/task/<task_id>/update-status', methods=['POST'])
@login_required
def ui_update_status(task_id):
    user_email = session.get('user_email')
    status = request.form.get('status')
    if status:
        success, msg = update_task_status(task_id, status, user_email)
        flash(msg)
    return redirect(url_for('ui_task_details', task_id=task_id))

@app.route('/update-status-home/<task_id>', methods=['POST'])
@login_required
def ui_update_status_home(task_id):
    user_email = session.get('user_email')
    status = request.form.get('status')
    if status:
        success, msg = update_task_status(task_id, status, user_email)
        flash(msg)
    return redirect(url_for('ui_home'))

@app.route('/stop-live-home/<task_id>', methods=['POST'])
@login_required
def ui_stop_live_home(task_id):
    user_email = session.get('user_email')
    success, msg = stop_live_task(task_id, user_email)
    flash(msg)
    return redirect(url_for('ui_home'))

if __name__ == '__main__':
    os.makedirs('data', exist_ok=True)
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            import json
            json.dump({}, f)
    if not os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, 'w') as f:
            import json
            json.dump({}, f)
    if not os.path.exists('data/session.json'):
        with open('data/session.json', 'w') as f:
            import json
            json.dump({'current_email': None}, f)
    app.run(debug=True, port=5000)

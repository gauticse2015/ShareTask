from src.utils import load_data, save_data, TASKS_FILE, get_current_user
from datetime import datetime, timedelta
import csv
import time

def create_task(title, description, frequency, due_date, task_type='normal', user_email=None, start_time=None, duration=None):
    current_email = user_email or get_current_user()
    if not current_email:
        return False, "Please login first"
    tasks = load_data(TASKS_FILE)
    for t in tasks.values():
        if t.get('description') == description:
            return False, "Task description must be unique"
    for t in tasks.values():
        if t.get('owner') == current_email and t.get('title') == title:
            return False, "Task title must be unique for the user"
    task_id = str(max([int(k) for k in tasks.keys()] or [0]) + 1)
    task_data = {
        'owner': current_email,
        'title': title,
        'description': description,
        'frequency': frequency,
        'due_date': due_date,
        'created_at': str(datetime.now()),
        'shared_with': [],
        'statuses': {current_email: 'To Do'},
        'master_status': 'To Do',
        'comments': [],
        'task_type': task_type
    }
    if task_type == 'live':
        task_data['live_status'] = 'not_started'
        task_data['start_time'] = start_time  # iso for preconfig
        task_data['duration'] = duration  # mins, 0=indef
        task_data['participants'] = {}  # email: {'joined': ts, 'left': ts or None, 'duration': secs}
        task_data['live_mode'] = 'preconfigured' if start_time else 'dynamic'
    tasks[task_id] = task_data
    save_data(TASKS_FILE, tasks)
    return True, f"Task created: {title} (type: {task_type})"

def share_task(task_id, share_email, user_email=None):
    current_email = user_email or get_current_user()
    if not current_email:
        return False, "Please login first"
    tasks = load_data(TASKS_FILE)
    users = load_data('data/users.json')
    if task_id not in tasks:
        return False, "Task not found"
    if tasks[task_id]['owner'] != current_email:
        return False, "Not task owner"
    if share_email not in users:
        return False, "User to share with not registered"
    task = tasks[task_id]
    if share_email not in task['shared_with']:
        task['shared_with'].append(share_email)
        task['statuses'][share_email] = 'To Do'
        save_data(TASKS_FILE, tasks)
    return True, f"Task shared with {share_email}"

def update_task_status(task_id, status, user_email=None):
    current_email = user_email or get_current_user()
    if not current_email:
        return False, "Please login first"
    tasks = load_data(TASKS_FILE)
    if task_id not in tasks:
        return False, "Task not found"
    task = tasks[task_id]
    if current_email not in task['statuses']:
        return False, "No permission to update this task"
    if status not in ['To Do', 'In Progress', 'Done']:
        return False, "Invalid status"
    task['statuses'][current_email] = status
    statuses = task['statuses'].values()
    if all(s == 'Done' for s in statuses):
        task['master_status'] = 'Done'
    elif any(s == 'In Progress' for s in statuses):
        task['master_status'] = 'In Progress'
    else:
        task['master_status'] = 'To Do'
    save_data(TASKS_FILE, tasks)
    return True, "Status updated"

def add_comment(task_id, comment, tags=None, user_email=None):
    current_email = user_email or get_current_user()
    if not current_email:
        return False, "Please login first"
    tasks = load_data(TASKS_FILE)
    if task_id not in tasks:
        return False, "Task not found"
    task = tasks[task_id]
    if current_email not in task['statuses'] and current_email != task['owner']:
        return False, "No permission to comment"
    if tags is None:
        tags = []
    task['comments'].append({
        'user': current_email,
        'comment': comment,
        'timestamp': str(datetime.now()),
        'tags': tags
    })
    save_data(TASKS_FILE, tasks)
    return True, "Comment added"

def revoke_share(task_id, revoke_email, user_email=None):
    current_email = user_email or get_current_user()
    if not current_email:
        return False, "Please login first"
    tasks = load_data(TASKS_FILE)
    if task_id not in tasks:
        return False, "Task not found"
    task = tasks[task_id]
    if task['owner'] != current_email:
        return False, "Only owner can revoke share"
    if revoke_email not in task.get('shared_with', []):
        return False, "User not in shared list"
    task['shared_with'].remove(revoke_email)
    if revoke_email in task['statuses']:
        del task['statuses'][revoke_email]
    save_data(TASKS_FILE, tasks)
    return True, f"Share revoked from {revoke_email}"

def start_live_task(task_id, duration=None, user_email=None):
    current_email = user_email or get_current_user()
    if not current_email:
        return False, "Please login first"
    tasks = load_data(TASKS_FILE)
    if task_id not in tasks:
        return False, "Task not found"
    task = tasks[task_id]
    if task['owner'] != current_email:
        return False, "Only owner can start live task"
    if task.get('task_type') != 'live':
        return False, "Not a live task"
    if task['live_status'] != 'not_started':
        return False, "Task already started or ended"
    task['live_status'] = 'running'
    task['start_time'] = str(datetime.now())
    task['duration'] = duration  # minutes
    # auto join owner for dynamic/pre
    task.setdefault('participants', {})[current_email] = {
        'joined': task['start_time'],
        'left': None,
        'duration': 0
    }
    save_data(TASKS_FILE, tasks)
    return True, f"Live task started (duration: {duration} mins if set)"

def stop_live_task(task_id, user_email=None):
    current_email = user_email or get_current_user()
    if not current_email:
        return False, "Please login first"
    tasks = load_data(TASKS_FILE)
    if task_id not in tasks:
        return False, "Task not found"
    task = tasks[task_id]
    if task['owner'] != current_email:
        return False, "Only owner can stop live task"
    if task.get('task_type') != 'live' or task['live_status'] != 'running':
        return False, "Task not running"
    task['live_status'] = 'ended'
    # End all participants
    now = datetime.now()
    for email, p in task['participants'].items():
        if p['left'] is None:
            left_ts = now
            joined = datetime.fromisoformat(p['joined'])
            p['left'] = str(left_ts)
            p['duration'] = (left_ts - joined).total_seconds()
    save_data(TASKS_FILE, tasks)
    return True, "Live task stopped"

def checkin_live_task(task_id, user_email=None):
    current_email = user_email or get_current_user()
    if not current_email:
        return False, "Please login first"
    tasks = load_data(TASKS_FILE)
    if task_id not in tasks:
        return False, "Task not found"
    task = tasks[task_id]
    if task.get('task_type') != 'live' or task['live_status'] != 'running':
        return False, "Live task not active"
    if current_email == task['owner']:
        return False, "Owner cannot checkin"
    if current_email not in task.get('participants', {}):
        task.setdefault('participants', {})[current_email] = {
            'joined': str(datetime.now()),
            'left': None,
            'duration': 0
        }
    save_data(TASKS_FILE, tasks)
    return True, f"Checked in to live task as participant"

def leave_live_task(task_id, user_email=None):
    current_email = user_email or get_current_user()
    if not current_email:
        return False, "Please login first"
    tasks = load_data(TASKS_FILE)
    if task_id not in tasks:
        return False, "Task not found"
    task = tasks[task_id]
    if task.get('task_type') != 'live' or task['live_status'] != 'running':
        return False, "Live task not active"
    if current_email not in task.get('participants', {}):
        return False, "Not participating"
    now = datetime.now()
    p = task['participants'][current_email]
    if p['left'] is None:
        joined = datetime.fromisoformat(p['joined'])
        p['left'] = str(now)
        p['duration'] = (now - joined).total_seconds()
    save_data(TASKS_FILE, tasks)
    return True, f"Left live task (duration: {int(p['duration'])} secs)"

def get_live_status(task_id, user_email=None):
    current_email = user_email or get_current_user()
    if not current_email:
        return False, "Please login first", {}
    tasks = load_data(TASKS_FILE)
    if task_id not in tasks:
        return False, "Task not found", {}
    task = tasks[task_id]
    if task.get('task_type') != 'live':
        return False, "Not a live task", {}
    # Auto-start for preconfigured if time passed
    if task.get('live_mode') == 'preconfigured' and task.get('start_time') and task['live_status'] == 'not_started':
        start = datetime.fromisoformat(task['start_time'])
        if datetime.now() >= start:
            task['live_status'] = 'running'
            # auto join owner
            task.setdefault('participants', {})[task['owner']] = {
                'joined': str(datetime.now()),
                'left': None,
                'duration': 0
            }
            save_data(TASKS_FILE, tasks)
    # Auto-end if duration exceeded
    if task['live_status'] == 'running' and task['duration'] is not None and task['start_time'] and task['duration'] > 0:
        start = datetime.fromisoformat(task['start_time'])
        elapsed = (datetime.now() - start).total_seconds() / 60
        if elapsed > task['duration']:
            task['live_status'] = 'ended'
            # End participants
            now = datetime.now()
            for email, p in task.get('participants', {}).items():
                if p['left'] is None:
                    joined = datetime.fromisoformat(p['joined'])
                    p['left'] = str(now)
                    p['duration'] = (now - joined).total_seconds()
            save_data(TASKS_FILE, tasks)
    status = {
        'live_status': task['live_status'],
        'start_time': task.get('start_time'),
        'duration': task.get('duration'),
        'participants': task.get('participants', {}),
        'absent': [u for u in task.get('shared_with', []) + [task['owner']] if u not in task.get('participants', {}) and u != task['owner']]
    }
    return True, "Live status retrieved", status

def list_tasks(show_shared=False, user_email=None):
    current_email = user_email or get_current_user()
    if not current_email:
        return False, "Please login first", []
    tasks = load_data(TASKS_FILE)
    user_tasks = []
    for tid, task in tasks.items():
        if task['owner'] == current_email or current_email in task.get('shared_with', []):
            # trigger auto for live (pre/start/end)
            if task.get('task_type') == 'live':
                if task.get('live_mode') == 'preconfigured' and task.get('start_time') and task.get('live_status') == 'not_started':
                    start = datetime.fromisoformat(task['start_time'])
                    if datetime.now() >= start:
                        task['live_status'] = 'running'
                        task.setdefault('participants', {})[task['owner']] = {'joined': str(datetime.now()), 'left': None, 'duration': 0}
                if task['live_status'] == 'running' and task['duration'] is not None and task['start_time'] and task['duration'] > 0:
                    start = datetime.fromisoformat(task['start_time'])
                    elapsed = (datetime.now() - start).total_seconds() / 60
                    if elapsed > task['duration']:
                        task['live_status'] = 'ended'
                        now = datetime.now()
                        for email, p in task.get('participants', {}).items():
                            if p['left'] is None:
                                joined = datetime.fromisoformat(p['joined'])
                                p['left'] = str(now)
                                p['duration'] = (now - joined).total_seconds()
                save_data(TASKS_FILE, tasks)
            user_tasks.append((tid, task))
    return True, "Tasks listed", user_tasks

def generate_report(user_email=None):
    tasks = load_data(TASKS_FILE)
    report = "Task Status Report (as of " + str(datetime.now()) + ")\n\n"
    filtered_tasks = {}
    for tid, task in tasks.items():
        if user_email is None or task['owner'] == user_email or user_email in task.get('shared_with', []):
            filtered_tasks[tid] = task
            report += f"Task ID: {tid} - {task['title']} (Owner: {task['owner']}, Master: {task.get('master_status', 'To Do')})\n"
            report += "Statuses:\n"
            for user, stat in task['statuses'].items():
                report += f"  {user}: {stat}\n"
            report += "Comments:\n"
            for c in task.get('comments', []):
                report += f"  {c['user']} @ {c['timestamp']}: {c['comment']} (tags: {c.get('tags', [])})\n"
            if task.get('task_type') == 'live':
                report += f"Live Status: {task.get('live_status')}\n"
            report += "---\n"
    with open('data/task_report.txt', 'w') as f:
        f.write(report)
    with open('data/task_report.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Task ID', 'Title', 'Owner', 'Master Status', 'User', 'User Status', 'Comments', 'Live Status'])
        for tid, task in filtered_tasks.items():
            live_stat = task.get('live_status', '')
            for user, stat in task['statuses'].items():
                comments_str = '; '.join([f"{c['user']}: {c['comment']}" for c in task.get('comments', [])])
                writer.writerow([tid, task['title'], task['owner'], task.get('master_status', 'To Do'), user, stat, comments_str, live_stat])
    print("Report generated and 'emailed' (saved to data/task_report.txt). Excel CSV report ready for download (data/task_report.csv)")
    return True, report

def delete_task(task_id, user_email=None):
    current_email = user_email or get_current_user()
    if not current_email:
        return False, "Please login first"
    tasks = load_data(TASKS_FILE)
    if task_id not in tasks:
        return False, "Task not found"
    if tasks[task_id]['owner'] != current_email:
        return False, "Only owner can delete task"
    del tasks[task_id]
    save_data(TASKS_FILE, tasks)
    return True, "Task deleted"

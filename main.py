import argparse
import sys
from src.user import register_user, login_user, get_notifications
from src.task import create_task, share_task, update_task_status, list_tasks, revoke_share, add_comment, generate_report, start_live_task, stop_live_task, checkin_live_task, get_live_status, accept_shared_task, reject_shared_task

def main():
    parser = argparse.ArgumentParser(description='Shareable Task Tracker CLI')
    subparsers = parser.add_subparsers(dest='command')

    # Register
    reg = subparsers.add_parser('register', help='Register a user')
    reg.add_argument('--email', required=True)
    reg.add_argument('--password', required=True)
    reg.add_argument('--name', required=True)

    # Login
    login = subparsers.add_parser('login', help='Login')
    login.add_argument('--email', required=True)
    login.add_argument('--password', required=True)

    # Create task
    create = subparsers.add_parser('create-task', help='Create a task (type live for live contribution)')
    create.add_argument('--title', required=True)
    create.add_argument('--description', required=True)
    create.add_argument('--frequency', required=True, choices=['daily', 'weekly', 'monthly', 'one-time'])
    create.add_argument('--due-date', required=True)
    create.add_argument('--type', choices=['normal', 'live'], default='normal')
    create.add_argument('--category', choices=['sharing', 'assignment'], default='sharing')

    # Share task
    share = subparsers.add_parser('share-task', help='Share a task')
    share.add_argument('--task-id', required=True)
    share.add_argument('--email', required=True)

    # Revoke share
    revoke = subparsers.add_parser('revoke-share', help='Revoke task share from user (owner only)')
    revoke.add_argument('--task-id', required=True)
    revoke.add_argument('--email', required=True)

    # Accept/reject shared task (for pending state lifecycle)
    accept = subparsers.add_parser('accept-task', help='Accept pending shared task')
    accept.add_argument('--task-id', required=True)
    reject = subparsers.add_parser('reject-task', help='Reject pending shared task')
    reject.add_argument('--task-id', required=True)

    # Add comment
    comment = subparsers.add_parser('add-comment', help='Add comment/motivation to task')
    comment.add_argument('--task-id', required=True)
    comment.add_argument('--comment', required=True)

    # Update status
    update = subparsers.add_parser('update-status', help='Update task status')
    update.add_argument('--task-id', required=True)
    update.add_argument('--status', required=True, choices=['To Do', 'In Progress', 'Done'])

    # Live task commands
    start_live = subparsers.add_parser('start-live-task', help='Start live task (owner only, optional duration mins)')
    start_live.add_argument('--task-id', required=True)
    start_live.add_argument('--duration', type=int, help='Optional duration in minutes')

    stop_live = subparsers.add_parser('stop-live-task', help='Stop live task (owner only)')
    stop_live.add_argument('--task-id', required=True)

    checkin_live = subparsers.add_parser('checkin-live-task', help='Checkin/join live task (shared users)')
    checkin_live.add_argument('--task-id', required=True)

    live_status = subparsers.add_parser('live-status', help='Check live task status (joined/in/absent etc)')
    live_status.add_argument('--task-id', required=True)

    # Generate report
    report = subparsers.add_parser('generate-report', help='Generate task status report (simulates Monday email)')

    # List tasks
    lst = subparsers.add_parser('list-tasks', help='List all tasks (own created + shared with user)')
    lst.add_argument('--shared', action='store_true', help='Deprecated: now always included')

    # Notifications (due dates, shares, rejections)
    notifs = subparsers.add_parser('notifications', help='View user notifications')

    args = parser.parse_args()

    if args.command == 'register':
        success, msg = register_user(args.email, args.password, args.name)
        if success:
            print(msg)
        else:
            print(f"ERROR: {msg}")
            sys.exit(1)
    elif args.command == 'login':
        success, msg = login_user(args.email, args.password)
        if success:
            print(msg)
        else:
            print(f"ERROR: {msg}")
            sys.exit(1)
    elif args.command == 'create-task':
        success, msg = create_task(args.title, args.description, args.frequency, args.due_date, args.type, args.category)
        if success:
            print(msg)
        else:
            print(f"ERROR: {msg}")
            sys.exit(1)
    elif args.command == 'share-task':
        success, msg = share_task(args.task_id, args.email)
        if success:
            print(msg)
        else:
            print(f"ERROR: {msg}")
            sys.exit(1)
    elif args.command == 'revoke-share':
        success, msg = revoke_share(args.task_id, args.email)
        if success:
            print(msg)
        else:
            print(f"ERROR: {msg}")
            sys.exit(1)
    elif args.command == 'accept-task':
        success, msg = accept_shared_task(args.task_id)
        if success:
            print(msg)
        else:
            print(f"ERROR: {msg}")
            sys.exit(1)
    elif args.command == 'reject-task':
        success, msg = reject_shared_task(args.task_id)
        if success:
            print(msg)
        else:
            print(f"ERROR: {msg}")
            sys.exit(1)
    elif args.command == 'add-comment':
        success, msg = add_comment(args.task_id, args.comment)
        if success:
            print(msg)
        else:
            print(f"ERROR: {msg}")
            sys.exit(1)
    elif args.command == 'update-status':
        success, msg = update_task_status(args.task_id, args.status)
        if success:
            print(msg)
        else:
            print(f"ERROR: {msg}")
            sys.exit(1)
    elif args.command == 'start-live-task':
        success, msg = start_live_task(args.task_id, args.duration)
        if success:
            print(msg)
        else:
            print(f"ERROR: {msg}")
            sys.exit(1)
    elif args.command == 'stop-live-task':
        success, msg = stop_live_task(args.task_id)
        if success:
            print(msg)
        else:
            print(f"ERROR: {msg}")
            sys.exit(1)
    elif args.command == 'checkin-live-task':
        success, msg = checkin_live_task(args.task_id)
        if success:
            print(msg)
        else:
            print(f"ERROR: {msg}")
            sys.exit(1)
    elif args.command == 'live-status':
        success, msg, status = get_live_status(args.task_id)
        if success:
            print(msg)
            print(status)
        else:
            print(f"ERROR: {msg}")
            sys.exit(1)
    elif args.command == 'list-tasks':
        success, msg, tasks = list_tasks(args.shared)
        if success:
            print(msg)
            for tid, task in tasks:
                print(f"Task ID: {tid}")
                print(f"  Owner: {task['owner']}")
                print(f"  Title: {task['title']}")
                print(f"  Master Status: {task.get('master_status', 'To Do')}")
                print(f"  Description: {task['description']}")
                print(f"  Frequency: {task['frequency']}")
                print(f"  Due: {task['due_date']}")
                print(f"  Statuses:")
                for user, stat in task['statuses'].items():
                    print(f"    {user}: {stat}")
                print(f"  Shared with: {task.get('shared_with', [])}")
                print("  Comments:")
                for c in task.get('comments', []):
                    print(f"    {c['user']} @ {c['timestamp']}: {c['comment']}")
                print("---")
        else:
            print(f"ERROR: {msg}")
            sys.exit(1)
    elif args.command == 'notifications':
        current = None
        try:
            from src.utils import get_current_user
            current = get_current_user()
        except:
            pass
        if not current:
            print("Please login first (no session)")
        else:
            notifs = get_notifications(current)
            print("Notifications:")
            for n in notifs:
                print(f"[{n.get('type', 'info').upper()}] {n.get('message')} @ {n.get('timestamp', '')[:16]}")
    elif args.command == 'generate-report':
        success, report = generate_report()
        if success:
            print(report)
        else:
            print(f"ERROR: {report}")
            sys.exit(1)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

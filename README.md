# Zed Base - Shareable Task Tracker CLI

## Project Overview
A CLI-based Shareable Task Tracker built in Python. Allows users to register, create recurring tasks, share them with others via email, update statuses, and view tasks.

## Initial Requirements
1. Register User
2. Create tasks with frequency (daily, weekly, monthly, etc.)
3. Share tasks with other registered users using email
4. Update task status: To Do, In Progress, Done
5. Check status of own tasks and shared tasks

## Development Plan
### Phase 1: Project Setup and Planning (Current)
- Define project structure
- Choose tech stack: Python 3, argparse for CLI, JSON for data storage, hashlib for passwords
- Create detailed plan and review

### Phase 2: Core Modules
- User management (register, login, store in users.json)
- Task management (create, update status, store in tasks.json)
- Sharing logic
- CLI commands

### Phase 3: Implementation
- Implement data models
- Build CLI interface
- Add basic validation and error handling

### Phase 4: Testing and Polish
- Basic tests
- Help messages, etc.

### Phase 5: Future Enhancements
- Reminders based on frequency
- Database (SQLite)
- Better auth
- GUI if needed

## Plan Review
**Strengths:**
- Simple and focused on core features
- Uses lightweight storage suitable for CLI
- Modular design for easy extension

**Potential Improvements/ Risks:**
- JSON file concurrency issues (mitigate with locking if needed, but single-user CLI ok initially)
- Password security (use bcrypt later)
- No real email validation/sending yet
- Task frequencies not automated yet

**Decision:** Plan approved. Proceed to development after this review. Start with setup.

## Complete Features
- **User Management**: Register/login with email validation, strong password (min 10 chars, upper/num/special), session handling.
- **Task Creation**: Title/desc unique (per-user/global), frequency, due, status (To Do/In Progress/Done), type (normal/live).
- **Sharing**: Share/revoke by email, per-user statuses.
- **Updates/Checks**: Status update, list (own+shared with owner/master/comments).
- **Comments/Tags**: Motivate/challenge with @tags.
- **Live Tasks**: Owner start (opt duration auto-end), shared checkin (participants track duration), status shows joined/in/left/absent.
- **Master Status**: Dynamic (Done only all Done; In Progress if any; else To Do).
- **Reporting**: Text + CSV (Excel-openable) status report (simulates weekly Mon 9AM IST email; use cron for scheduling).
- **Testing**: Bash script (test.sh) for pos/neg flows, logs (test.log) with exits/ERROR prefixes, preserves data.
- **Storage**: Organized in data/ dir (JSON persistence, no deletes in tests).

## Project Structure
```
zed-base/
├── README.md
├── main.py              # CLI entry with argparse
├── test.sh              # Bash E2E test script (pos/neg, logs; preserves data)
├── src/                 # Core modules
│   ├── __init__.py
│   ├── user.py          # Register/login/validation
│   ├── task.py          # Tasks, live, comments, reports
│   └── utils.py         # Data I/O, hash, validators
├── data/                # Organized storage (moved from root)
│   ├── users.json       # Users data
│   ├── tasks.json       # Tasks (incl live/participants)
│   ├── session.json     # Current login session
│   ├── task_report.txt  # Text report
│   └── task_report.csv  # Excel-compatible CSV report
├── tests/               # (placeholder for future unit tests)
└── requirements.txt     # (empty, stdlib only)
```

## Future Plan
- Frequency-based reminders/notifications (e.g., via cron/email).
- Migrate to SQLite DB for better concurrency/scalability.
- Enhance auth (bcrypt, JWT sessions).
- Real SMTP email integration.
- Web/GUI frontend (Flask/Django).
- Unit tests (pytest), CI/CD.
- Docker/containerization for deployment.

Data/ structure ensures clean root, easy backup. All features implemented/tested per queries.

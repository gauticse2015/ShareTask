#!/bin/bash

LOG_FILE="test.log"
echo "=== Task Tracker Test Script Started at $(date) ===" > $LOG_FILE
echo "Running positive and negative scenarios with improved logging and exit codes..." >> $LOG_FILE
echo "" >> $LOG_FILE

# Function to run command and log with readability (captures true exit code)
run_test() {
    local test_name="$1"
    local cmd="$2"
    echo "=== TEST CASE: $test_name ===" | tee -a $LOG_FILE
    echo "Command: $cmd" | tee -a $LOG_FILE
    echo "Output:" >> $LOG_FILE
    # Capture output and real exit (avoid pipe last-cmd override)
    output=$(eval "$cmd" 2>&1)
    local exit_code=$?
    echo "$output" | tee -a $LOG_FILE
    echo "Exit code: $exit_code" >> $LOG_FILE
    if [ $exit_code -eq 0 ]; then
        echo "STATUS: SUCCESS" | tee -a $LOG_FILE
    else
        echo "STATUS: FAILURE" | tee -a $LOG_FILE
    fi
    echo "----------------------------------------" >> $LOG_FILE
    echo "" >> $LOG_FILE
}

# Positive scenarios
echo "=== Positive Scenarios ===" >> $LOG_FILE
run_test "Register new user (pos)" "python3 main.py register --email testpos12@example.com --password Pass123!test --name PosUser1"
run_test "Login valid user (pos)" "python3 main.py login --email testpos12@example.com --password Pass123!test"
run_test "Create task unique (pos)" "python3 main.py create-task --title 'Pos Task New' --description 'Pos desc unique $(date +%s)' --frequency daily --due-date '2025-01-01'"
run_test "Register second user (pos)" "python3 main.py register --email testpos23@example.com --password Pass123!test --name PosUser2"
run_test "Share task (pos)" "python3 main.py login --email testpos23@example.com --password Pass123!test && python3 main.py share-task --task-id 2 --email testpos23@example.com"  # use recent ID
run_test "Add comment with tag (pos)" "python3 main.py add-comment --task-id 2 --comment 'Motivating progress!' --tags testpos2@example.com"
run_test "Update status (pos)" "python3 main.py update-status --task-id 2 --status 'In Progress'"
run_test "List tasks (pos)" "python3 main.py list-tasks"
run_test "Generate report CSV (pos)" "python3 main.py generate-report"

# Negative scenarios (expect ERROR and exit 1)
echo "=== Negative Scenarios ===" >> $LOG_FILE
run_test "Register invalid email (neg)" "python3 main.py register --email invalid-email --password short --name Bad"
run_test "Login invalid creds (neg)" "python3 main.py login --email nonexist@example.com --password wrong"
run_test "Create task dup desc (neg)" "python3 main.py create-task --title 'Dup' --description 'Pos desc unique' --frequency daily --due-date '2025-01-01'"
run_test "Update invalid task (neg)" "python3 main.py update-status --task-id 999 --status 'Done'"
run_test "Revoke invalid (neg)" "python3 main.py revoke-share --task-id 2 --email nonshared@example.com"
run_test "Comment invalid task (neg)" "python3 main.py add-comment --task-id 999 --comment 'No perm'"

echo "=== Test Script Completed at $(date) ===" >> $LOG_FILE
echo "Detailed logs in $LOG_FILE with SUCCESS/FAILURE and ERROR prefixes. Exit codes differentiated."

# Live task scenarios (pos/neg)
echo "=== Live Task Scenarios ===" >> $LOG_FILE
run_test "Create live task (pos)" "python3 main.py create-task --title 'Live Meeting-12' --description 'Live contrib test $(date +%s)' --frequency one-time --due-date '2025-01-01' --type live"
run_test "Start live task (pos)" "python3 main.py start-live-task --task-id 5 --duration 10"  # assume ID
run_test "Checkin as participant (pos)" "python3 main.py login --email testpos2@example.com --password Pass123!test && python3 main.py checkin-live-task --task-id 5"
run_test "Live status check (pos)" "python3 main.py live-status --task-id 5"
run_test "Stop live task (pos)" "python3 main.py login --email testpos1@example.com --password Pass123!test && python3 main.py stop-live-task --task-id 5"
run_test "Create non-live (neg for live)" "python3 main.py create-task --title 'Normal Task' --description 'Normal $(date +%s)' --frequency daily --due-date '2025-01-01'"
run_test "Start non-live (neg)" "python3 main.py start-live-task --task-id 6 --duration 5"
run_test "Checkin invalid live (neg)" "python3 main.py checkin-live-task --task-id 999"

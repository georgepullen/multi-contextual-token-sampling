import os
import re

LOG_FILE = "logs.txt"

async def apply_filter(text):
    filtered_text = re.sub(r"[^a-z0-9\s,.!?']", '', text.lower())
    return filtered_text

async def store_log(prompt, response, username):
    log_str = prompt + f'{response}"'
    with open(LOG_FILE, 'a') as file:
        file.write(log_str)

async def retrieve_logs(amount, users):
    if not os.path.exists(LOG_FILE):
        return {user: [] for user in users}

    with open(LOG_FILE, 'r') as file:
        logs = file.readlines()

    user_logs = {user: [] for user in users}

    for log in logs:
        pattern = r'\b(\w+)\b(?=\s+said)'
        matches = re.findall(pattern, log)
        username = "unknown"
        if matches:
            username = matches[0]
        if username in users:
            user_logs[username].append(log.strip())

    for user in user_logs:
        user_logs[user] = user_logs[user][-amount:]

    return user_logs

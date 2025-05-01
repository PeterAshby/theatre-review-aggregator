import os
from datetime import datetime

def log_schedule(message="Script run successfully"):
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(project_root, 'data')
    os.makedirs(data_dir, exist_ok=True)
    log_path = os.path.join(data_dir, 'schedule_log.txt')

    with open(log_path, 'a') as log:
        log.write(f'[{datetime.now()}] {message}\n')

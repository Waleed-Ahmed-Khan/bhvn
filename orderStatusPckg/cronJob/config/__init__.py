import os 
from pathlib import Path

PO_UPDATE_DAYS = 360
LOGS_DIR_NAME = "Logs"
LOGS_FILE_NAME = "etl_logs.log"
LOCK_FILLOCK_FILE_PATH = os.path.join('orderStatusPckg', 'cronJob', 'main.py.lock')

LOGS_BASE_DIR = Path(os.path.join("orderStatusPckg",'cronJob', LOGS_DIR_NAME)).resolve().absolute()
os.makedirs(LOGS_BASE_DIR, exist_ok=True)
LOGS_FILE_PATH = os.path.join(LOGS_BASE_DIR, LOGS_FILE_NAME)


#LOGS_FILE_PATH = os.path.join(LOGS_DIR_NAME, LOGS_FILE_NAME)

from pathlib import Path
import os

DUE_THRESHOLD_DAYS = 2
OVERDUE_THRESHOLD = -2
LOGS_DIR_NAME = "Logs"
LOGS_FILE_NAME = "etl_logs.log"
CSV_DIR_NAME = "csvDir"
PURCH_DET_CSV_FILE_NAME = "Pending Purchase Detail.xlsx"
COMPLETE_MFG_CSV_FILE_NAME = "End-to-end Mfg Status.xlsx"


LOGS_DIR = Path(os.path.join("purchasePckg","cronJobs", "leadtimeAlert",  LOGS_DIR_NAME)).resolve().absolute()
os.makedirs(LOGS_DIR, exist_ok=True)
CSV_DIR = Path(os.path.join("purchasePckg","cronJobs", "leadtimeAlert",  CSV_DIR_NAME)).resolve().absolute()
os.makedirs(CSV_DIR, exist_ok=True)
LOCK_FILLOCK_FILE_PATH = os.path.join('purchasePckg', 'cronJobs', 'leadtimeAlert', 'main.py.lock')
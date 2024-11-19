from pathlib import Path
import os

DUE_THRESHOLD_DAYS = 80
OVERDUE_THRESHOLD = -80
LOGS_DIR_NAME = "Logs"
LOGS_FILE_NAME = "order_due_date_alert_logs.log"
CSV_DIR_NAME = "csvDir"
SALES_DET_CSV_FILE_NAME = "Sales Details Detail.xlsx"
COMPLETE_MFG_CSV_FILE_NAME = "End-to-end Mfg Status.xlsx"


LOGS_DIR = Path(os.path.join("salesPckg","cronJobs", "leadtimeAlert",  LOGS_DIR_NAME)).resolve().absolute()
os.makedirs(LOGS_DIR, exist_ok=True)
CSV_DIR = Path(os.path.join("salesPckg","cronJobs", "leadtimeAlert",  CSV_DIR_NAME)).resolve().absolute()
os.makedirs(CSV_DIR, exist_ok=True)

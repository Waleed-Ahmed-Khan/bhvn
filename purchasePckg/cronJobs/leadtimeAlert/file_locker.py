import arrow
import purchasePckg.cronJobs.leadtimeAlert.config as CONFIG
import os
from pathlib import Path
from appLogger import AppLogger


class LocksManager:
    def __init__(self):
        self.lock_file = CONFIG.LOCK_FILLOCK_FILE_PATH
        self.logger = AppLogger()
        LOGS_BASE_DIR = Path(os.path.join("orderStatusPckg",'cronJob', CONFIG.LOGS_DIR_NAME)).resolve().absolute()
        os.makedirs(LOGS_BASE_DIR, exist_ok=True)
        self.logs_file = os.path.join(LOGS_BASE_DIR, CONFIG.LOGS_FILE_NAME)

    def if_locked(self):
        if os.path.exists(self.lock_file):
            print(arrow.get(tzinfo='UTC'))
            criticalTime = arrow.get(tzinfo='UTC').shift(hours=-5)
            print(criticalTime)
            itemTime = arrow.get(Path(self.lock_file).stat().st_mtime)
            print(itemTime)
            if criticalTime > itemTime:
                with open(self.logs_file, 'a+') as file:
                    self.logger.log(file, f"Lock Opened; critital time is {criticalTime} which is greater than the file modification time {itemTime}")
                    self.remove_lock_file()
                return False
            else:
                with open(self.logs_file, 'a+') as file:
                    self.logger.log(file, f"Could not open the file lock; critital time is {criticalTime} which is less than the file modification time {itemTime}")
                return True
        else:
            with open(self.logs_file, 'a+') as file:
                self.logger.log(file, "Lock file is not available, creating a new lock file...")
                
            return False
        
    def remove_lock_file(self):
        if os.path.exists(self.lock_file):
            os.remove(self.lock_file)
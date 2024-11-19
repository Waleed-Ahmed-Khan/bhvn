import sys, os
from pathlib import Path
FILE = Path(__file__).resolve()
ROOT = FILE.parents[3]  
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT)) 


from appLogger import AppLogger
from purchasePckg.cronJobs.leadtimeAlert.pipeline import Pipeline
from purchasePckg.cronJobs.leadtimeAlert.extract import Loader
import purchasePckg.cronJobs.leadtimeAlert.config as CONFIG
from purchasePckg.cronJobs.leadtimeAlert.mail import Email
from purchasePckg.cronJobs.leadtimeAlert.file_locker import LocksManager


import fasteners
import threading

logger = AppLogger()
#LOGS_BASE_DIR = Path(os.path.join("purchasePckg",'cronJobs', 'leadtimeAlert', CONFIG.LOGS_DIR_NAME)).resolve().absolute()
LOGS_BASE_DIR = CONFIG.LOGS_DIR
os.makedirs(LOGS_BASE_DIR, exist_ok=True)
logs_file = os.path.join(LOGS_BASE_DIR, CONFIG.LOGS_FILE_NAME)
thread_lock = threading.Lock() 

def run():
    try:
        logger = AppLogger()
        locks_manager = LocksManager()
        logs_file = os.path.join(CONFIG.LOGS_DIR, CONFIG.LOGS_FILE_NAME)
        if locks_manager.if_locked():
            with open(logs_file, 'a+') as file:
                logger.log(file, "########### Terminating the job as the file is locked ###########")
                sys.exit(0)
        thread_lock.acquire()
        with fasteners.InterProcessLock(CONFIG.LOCK_FILLOCK_FILE_PATH):
            with open(logs_file, 'a+') as file:
                logger.log(file, "Started ETL job for Purchase lead-time alert...")
            loader = Loader()
            sales_df = loader.get_sales_df()
            if sales_df.empty:
                with open(logs_file, 'a+') as file:
                    logger.log(file, "Terminating the Pipeline as there are no overdue or upcoming orders")
                sys.exit()
            purchase_df = loader.get_purchase_df()
            pos_sales = loader.pos_sales
            pos_purchase = loader.pos_purchase
            with open(logs_file, 'a+') as file:
                logger.log(file, f"Found {len(pos_sales)} POs of Sales and {len(pos_purchase)} POs of Purchase with the sales po numbers {pos_sales} and the purchase po numbers {pos_purchase}")
            for po in pos_purchase:
                with open(logs_file, 'a+') as file:
                    logger.log(file, f"Creating the pipeline instance for PO: {po}")
                pipeline = Pipeline(sales_df , purchase_df, po)
                with open(logs_file, 'a+') as file:
                    logger.log(file, f"Transforming data for PO: {po}")
                pipeline.transform()
                with open(logs_file, 'a+') as file:
                    logger.log(file, f"Sending alert for : {po}")
                pipeline.send_alert()
            with open(logs_file, 'a+') as file:
                logger.log(file, "#################### Pipeline has been executed successfully ####################")
    except Exception as e:
        with open(logs_file, 'a+') as file:
            logger.log(file, f"Error : {str(e)}")
        from pipelineAlerts import Email
        alert = Email()
        alert.pipeline_failure_alert(subject="Purchase Lead-time alert pipeline failed", error = str(e))
        with open(logs_file, 'a+') as file:
            logger.log(file, "Pipeline failure alert sent!")
            logger.log(file, "!!!!!!!!!!!!!! Pipeline failed !!!!!!!!!!!!!!")
        raise e

if __name__ == "__main__":
    run()
thread_lock.release()
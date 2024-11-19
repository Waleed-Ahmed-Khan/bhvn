import sys, os
from pathlib import Path
FILE = Path(__file__).resolve()
ROOT = FILE.parents[2]  
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT)) 

from utils.sys_logging import get_logger
from appLogger import AppLogger
from orderStatusPckg.cronJob.pipeline import Pipeline
from orderStatusPckg.cronJob.update import Updator
from orderStatusPckg.cronJob.load import LoaderOLAP
import orderStatusPckg.cronJob.config as CONFIG
from orderStatusPckg.cronJob.file_locker import LocksManager
from pipelineAlerts import Email
import fasteners
import threading

logger = get_logger(CONFIG.LOGS_FILE_PATH)

#logger = AppLogger()
#LOGS_BASE_DIR = Path(os.path.join("orderStatusPckg",'cronJob', CONFIG.LOGS_DIR_NAME)).resolve().absolute()
#os.makedirs(LOGS_BASE_DIR, exist_ok=True)
#logs_file = os.path.join(LOGS_BASE_DIR, CONFIG.LOGS_FILE_NAME)
thread_lock = threading.Lock() 
def run():
    try:
        locks_manager = LocksManager()
        if locks_manager.if_locked():
            logger.info("########### Terminating the job as the file is locked ###########")
            sys.exit(0)
        thread_lock.acquire()
        with fasteners.InterProcessLock(CONFIG.LOCK_FILLOCK_FILE_PATH):
            logger.info("Started ETL job for OrderStatus(Mgf Life Cycle)...")
            updater = Updator()
            loader = LoaderOLAP()
            pos_to_update = updater.pos_to_update
            #pos_to_update = ["2022-BG-100-1"]
            logger.info(f"POs to be update are {len(pos_to_update)} with the list {pos_to_update}")
            for po in pos_to_update:
                logger.info(f"Deleting the old data for PO: {po}")
                updater.dlt_previous_data_olap(po)
                pipeline = Pipeline(po)
                logger.info(f"Extracting data for PO: {po}")
                pipeline.extract()
                logger.info(f"Transforming data for PO: {po}")
                pipeline.transform()
                logger.info(f"Inserting New data for PO: {po}")
                pipeline.load(loader)
            logger.info("#################### Pipeline has been executed successfully ####################")
    except Exception as e:
        logger.info(f"Error : {str(e)}")
        alert = Email()
        alert.pipeline_failure_alert(subject="Order Status ETL(MFG life cycle) pipeline failed", error = str(e))
        logger.error("Pipeline failure alert sent!")
        logger.error("!!!!!!!!!!!!!! Pipeline failed !!!!!!!!!!!!!!")
        raise e

if __name__ == "__main__":
    run()
thread_lock.release()
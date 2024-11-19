import sys, os
from pathlib import Path
FILE = Path(__file__).resolve()
ROOT = FILE.parents[3]  
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT)) 


from appLogger import AppLogger
from salesPckg.cronJobs.leadtimeAlert.pipeline import Pipeline
from salesPckg.cronJobs.leadtimeAlert.extract import Loader
import salesPckg.cronJobs.leadtimeAlert.config as CONFIG
from salesPckg.cronJobs.leadtimeAlert.mail import Email



def run():
    try:
        logger = AppLogger()
        logs_file = os.path.join(CONFIG.LOGS_DIR, CONFIG.LOGS_FILE_NAME)
        with open(logs_file, 'a+') as file:
            logger.log(file, "Started ETL job for Sales lead-time alert...")
        loader = Loader()
        sales_df = loader.get_sales_df()
        #purchase_df = loader.get_purchase_df()
        pos_sales = loader.pos_sales
        #pos_purchase = loader.pos_purchase
        with open(logs_file, 'a+') as file:
            logger.log(file, f"Found {len(pos_sales)} POs of Sales po numbers {pos_sales}")
        for po in pos_sales:
            with open(logs_file, 'a+') as file:
                logger.log(file, f"Creating the pipeline instance for PO: {po}")
            pipeline = Pipeline(sales_df , po)
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
        alert.pipeline_failure_alert(subject="Sales Lead-time alert pipeline failed", error = str(e))
        with open(logs_file, 'a+') as file:
            logger.log(file, "Pipeline failure alert sent!")
            logger.log(file, "!!!!!!!!!!!!!! Pipeline failed !!!!!!!!!!!!!!")
        raise e

if __name__ == "__main__":
    run()
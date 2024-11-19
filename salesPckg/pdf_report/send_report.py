import sys
sys.path.append("..")
from generate_report import GenerateReport
from dotenv import load_dotenv
import os,  datetime, pytz, smtplib
from pathlib import Path
from loader import LoadData
from email.message import EmailMessage
from appLogger import AppLogger
from pipelineAlerts import Email
import arrow 

load_dotenv()
EMAIL_PASS = os.getenv('EMAIL_PASS')
LOGS_DIR = "logs"
FILE = "sales_pdf_logs.txt"
class Report:
    def __init__(self):
        self.logger = AppLogger()
        self.LOGS_BASE_DIR = Path(os.path.join("salesPckg",'pdf_report', LOGS_DIR)).resolve().absolute()
        os.makedirs(self.LOGS_BASE_DIR, exist_ok=True)
        self.logs_file = os.path.join(self.LOGS_BASE_DIR, FILE)
        with open(self.logs_file, 'a+') as file:
            self.logger.log(file, "Sales PDF Report job started...")
        self.SENDER = 'donotreply.bhvn.ml@gmail.com'
        self.PASSWORD = EMAIL_PASS 
        self.RECEIVER = ['hasnain@bhgloves.com', 'hasnainmehmood3435@gmail.com']
        #self.RECEIVER = ['khalid@bhgloves.com','alibutt@bhgloves.com', 'hr@bhgloves.com','rizwan@bhgloves.com', 'compliance.vn@bhgloves.com','hr.assistant@bhgloves.com', 'hr.assistant1@bhgloves.com', 'production.binh@bhgloves.com', 'asad@bhgloves.com', 'costing@bhgloves.com','quality@bhgloves.com','processing@bhgloves.com', 'packing@bhgloves.com','production@bhgloves.com', 'hasnain@bhgloves.com']
        self.BASE_PATH = Path(os.path.join("salesPckg", "pdf_report")).resolve().absolute()
        self.HTML_TEMPLATE_PATH = Path(os.path.join(self.BASE_PATH, "email_template.html")).resolve().absolute()
        self.lock_file = Path(os.path.join(self.BASE_PATH,'main.py.lock')).resolve().absolute()

        self.date_vn = datetime.datetime.now(pytz.timezone("Asia/Jakarta")).strftime("%d %b, %Y")
        self.pdf_files = [f"Sales Report on {self.date_vn}.pdf"]

    def send_email(self):

        try:
            GenerateReport(f"Sales Report on {self.date_vn}.pdf", self.logs_file).complete_report()
            #LoadData(load_data=False).remove_csvs()
            #LoadData(load_data=False).remove_plots()
            msg = EmailMessage()
            msg["Subject"] = "Weekly Status Report"
            msg["From"] = self.SENDER
            msg["To"] = self.RECEIVER


            with open(self.HTML_TEMPLATE_PATH, "r") as f:
                html_content = f.read()
            
            msg.set_content(html_content, subtype="html")
            
            #msg.add_alternative("Please find attachement for HR Daily report")

            for file_ in self.pdf_files:
                path = os.path.join(self.BASE_PATH, 'reports', file_)
                with open(path, "rb") as f:
                    file_data = f.read()
                    file_name = file_

                msg.add_attachment(file_data, maintype="application", 
                subtype="octet-stream", filename=file_name)

            with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
                smtp.starttls()
                smtp.login(self.SENDER, self.PASSWORD)
                with open(self.logs_file, 'a+') as file:
                    self.logger.log(file, "Email Login Successfull...")
                print("log in successfull!! \nsending email")
                #smtp.send_message(msg)
                with open(self.logs_file, 'a+') as file:
                    self.logger.log(file, f"Successfully sent email to {self.RECEIVER}")
                print(f"email Sent to {self.RECEIVER}")
                #LoadData(load_data=False).dlt_report()
                with open(self.logs_file, 'a+') as file:
                    self.logger.log(file, "Removed CSV files")
                    self.logger.log(file, "*************** Job Completed Successfully ***************")
        except Exception as e:
            with open(self.logs_file, 'a+') as file:
                self.logger.log(file, f"Error : {str(e)}")
            LoadData(load_data=False).remove_csvs()
            alert = Email()
            alert.pipeline_failure_alert(subject="Sales PDF Report Pipeline Failed", error = str(e))
            with open(self.logs_file, 'a+') as file:
                self.logger.log(file, "Pipeline failure alert sent!")
                self.logger.log(file, "!!!!!!!!!!!!!! Pipeline failed !!!!!!!!!!!!!!")
            raise e

    def if_locked(self):
        if self.lock_file.exists():
            print(arrow.get(tzinfo='UTC'))
            criticalTime = arrow.get(tzinfo='UTC').shift(minutes=-5)
            print(criticalTime)
            itemTime = arrow.get(self.lock_file.stat().st_mtime)
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
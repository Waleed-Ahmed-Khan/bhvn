import sys
sys.path.append(".")

import os
import smtplib
from email.message import EmailMessage
from pathlib import Path

from dotenv import load_dotenv
from sqlDBOperations import sqlDBManagement

from appLogger.logger import AppLogger
from pipelineAlerts import Email
import arrow, fasteners

load_dotenv()
EMAIL_PASS = os.getenv('EMAIL_PASS')
SENDER = 'donotreply.bhvn.ml@gmail.com'

OLAP_HOST = os.getenv('OLAP_HOST')
OLAP_DB_NAME = os.getenv('OLAP_DB_NAME')
OLAP_USER_NAME = os.getenv('OLAP_USER_NAME')
OLAP_MYSQL_PASS = os.getenv('OLAP_MYSQL_PASS')
#CRON_PATH = "/home/hasnain/distorted/bhvnbi/cronJobs"
#with portalocker.Lock(Path(os.path.join('cronJobs','pass_update_req.py')).resolve().absolute(), 'rb+', timeout=120) as fh:
    # do what you need to do
class PassUpdateReq:
    def __init__(self):
        LOGS_DIR = os.path.join('cronJobs', 'logs')
        self.LOGS_DIR = Path(LOGS_DIR).resolve().absolute()
        #logs_dir = os.path.join(Path(CRON_PATH).resolve(), "logs")
        os.makedirs(self.LOGS_DIR, exist_ok=True)
        self.query = f""" SELECT name, email FROM tblusers WHERE pwd IN ("blue!!!", "Ringdas321", "123", "321", "blue@321", "blue@123") """
        self.logs_file = os.path.join(self.LOGS_DIR, 'passUpdateRequiredLogs.txt')
        self.lock_file = Path(os.path.join('cronJobs','pass_update_req_main.py.lock')).resolve().absolute()
        self.logger = AppLogger()

    def get_weak_pass(self):
        mysql = sqlDBManagement(host=OLAP_HOST,
                        username=OLAP_USER_NAME,
                        password=OLAP_MYSQL_PASS,
                        database=OLAP_DB_NAME)

        self.user_data = mysql.getDataFramebyQuery(self.query)
        
        with open(self.logs_file, 'a+') as file:
            self.logger.log(file, f"User Emails with the weak passwords {self.user_data['email'].tolist()}")

        if self.user_data.empty:
            with open(self.logs_file, 'a+') as file:
                self.logger.log(
                    file, "########### Terminating the job as there are no accounts with weak passwords ###########")
            sys.exit(0)

    def generate_msg(self):
        name = self.row['name']
        self.receiver = self.row['email']
        self.msg = EmailMessage()
        self.msg["Subject"] = "Security Action Required"
        self.msg["From"] = SENDER
        self.msg["To"] = self.receiver
        body = f"""

        Hi {name},

        You are either using a default or a weak password for http://ml.bhgloves.com/, which leaves a vulnerability in the system.
        Go to http://ml.bhgloves.com/, search for "Update password" in the sidebar on left, and set a strong password.
        
        Please take action as early as possible to avoid your account getting blocked.
        Should you need any further information/help, please do not hesitate to contact admin at hasnain@bhgloves.com

        Note: Do not reply to this email as this is a system-generated alert.

        Regards,
        BHVN ML
        """
        self.msg.set_content(body) 

    def send_msg(self):
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            # smtp.starttls()
            smtp.login(SENDER, EMAIL_PASS)
            print(f"Log in successfull!! \nSending email to {self.receiver}...")
            smtp.send_message(self.msg)
            print(f'Email sent to {self.receiver}')
            with open(self.logs_file, 'a+') as file:
                self.logger.log(file, f'Email Sent to "{self.receiver}"')
                
    def email_delivery(self):
        for index, self.row in self.user_data.iterrows():
            try:
                self.generate_msg()
                self.send_msg()
            except Exception as e:
                try:
                    with open(self.logs_file, 'a+') as file:
                        self.logger.log(
                            file, f'Could not send the email to "{self.receiver}". Error: {e}')
                except (UnboundLocalError, NameError):
                    with open(self.logs_file, 'a+') as file:
                        self.logger.log(
                            file, f'Could not finish weak password update requirement job. Error: {e}')

                alert = Email()
                alert.pipeline_failure_alert(
                    subject="Weak password update requirement job failed", error=str(e))
                with open(self.logs_file, 'a+') as file:
                    self.logger.log(file, "Pipeline failure alert sent!")
                    self.logger.log(file, "!!!!!!!!!!!!!! Pipeline failed !!!!!!!!!!!!!!")

                raise e
        with open(self.logs_file, 'a+') as file:
            self.logger.log(file, "********************** Job Completed Successfully **********************")
        sys.exit(0)

    def if_locked(self):
        if self.lock_file.exists():
            print(arrow.get(tzinfo='UTC'))
            criticalTime = arrow.get(tzinfo='UTC').shift(hours=-5)
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
        
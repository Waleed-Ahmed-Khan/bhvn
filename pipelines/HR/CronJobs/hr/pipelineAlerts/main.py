
from dotenv import load_dotenv
import os,  datetime, pytz, smtplib
from email.message import EmailMessage

load_dotenv()
EMAIL_PASS = os.getenv('EMAIL_PASS')
SENDER = 'donotreply.bhvn.ml@gmail.com'
CLIENT = 'hasnain@bhgloves.com'

class Email:
    def __init__(self): 
        self.password = EMAIL_PASS 
        self.name = 'Hasnain'
        self.sender = SENDER
        self.receiver = CLIENT
        self.datetime = datetime.datetime.now(pytz.timezone("Asia/Jakarta")).strftime("%m/%d/%Y, %H:%M:%S")
        
    def pipeline_failure_alert(self, subject, error):
        try:
            msg = EmailMessage()
            msg["Subject"] = subject
            msg["From"] = self.sender
            msg["To"] = self.receiver

            body = f"""

Hi {self.name},

Pipeline has failed at {self.datetime} Vietnam Local Time.
Please take action.

Error : 
{error}
 
Note: Do not reply to this email as this is a system-generated alert.

Regards,
BHVN DE
            """
            msg.set_content(body)

            with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
                smtp.starttls()
                smtp.login(self.sender, self.password)
                print("log in successfull!! \nsending email")
                smtp.send_message(msg)
                print("email Sent")

        except Exception as e:
            raise e
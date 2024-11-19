
from dotenv import load_dotenv
import os,  datetime, pytz, smtplib
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import config as CONFIG

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
        
    def send_alert(self, subject, mime_text):
        try:
            #msg = EmailMessage()
            msg = MIMEMultipart()
            msg["Subject"] = subject
            msg["From"] = self.sender
            msg["To"] = self.receiver
            msg.attach(mime_text)

            SALES_DET_FILE_PATH = os.path.join(CONFIG.CSV_DIR, CONFIG.SALES_DET_CSV_FILE_NAME)
            COMPLETE_MFG_PATH = os.path.join(CONFIG.CSV_DIR, CONFIG.COMPLETE_MFG_CSV_FILE_NAME)
            
            try:
                with open(SALES_DET_FILE_PATH, "rb") as attachment:
                    p = MIMEApplication(attachment.read(),_subtype="csv")	
                    p.add_header('Content-Disposition', f"attachment; filename= {CONFIG.SALES_DET_CSV_FILE_NAME}")
                    msg.attach(p)
                with open(COMPLETE_MFG_PATH, "rb") as attachment:
                    p = MIMEApplication(attachment.read(),_subtype="csv")	
                    p.add_header('Content-Disposition', f"attachment; filename= {CONFIG.COMPLETE_MFG_CSV_FILE_NAME}")
                    msg.attach(p)
            except FileNotFoundError:
                pass
            except Exception as e:
                raise e
            

            with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
                smtp.starttls()
                smtp.login(self.sender, self.password)
                print("log in successfull!! \nsending email")
                smtp.sendmail(msg['From'], msg['To'] , msg.as_string())
                #smtp.send_message(msg)
                print("email Sent")

        except Exception as e:
            raise e
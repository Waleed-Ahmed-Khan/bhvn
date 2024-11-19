
from dotenv import load_dotenv
import os,  datetime, pytz, smtplib
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import config as CONFIG

load_dotenv()
EMAIL_PASS = os.getenv('EMAIL_PASS')
SENDER = 'donotreply.bhvn.ml@gmail.com'
CLIENT = ['purchase.assistant@bhgloves.com', 'chien.qc@bhgloves.com', 'alibutt@bhgloves.com', 'production.binh@bhgloves.com', 'rizwan@bhgloves.com', 'imran@bhgloves.com', 'asad@bhgloves.com','costing@bhgloves.com', 'merchandiser@bhgloves.com','export.assistant@bhgloves.com', 'purchase01@bhgloves.com', 'hasnain@bhgloves.com']
#CC = ['ahsan@bhgloves.com','ahmad@bhgloves.com']
#CLIENT = ['hasnain@bhgloves.com']
#CC = ['hasnain@bhgloves.com', "hasanain@aicaliber.com"]
CC = ['ar@bhgloves.com', 'khalid@bhgloves.com', 'ahmad@bhgloves.com', 'ahsan@bhgloves.com']
class Email:
    def __init__(self): 
        self.password = EMAIL_PASS 
        self.name = 'Hasnain'
        self.sender = SENDER
        self.receiver = ", ".join(CLIENT)
        self.cc = ", ".join(CC)
        self.datetime = datetime.datetime.now(pytz.timezone("Asia/Jakarta")).strftime("%m/%d/%Y, %H:%M:%S")
        
    def send_alert(self, subject, body, mime_text):
        try:
            #msg = EmailMessage()
            msg = MIMEMultipart()
            msg["Subject"] = subject
            msg["From"] = self.sender
            msg["To"] = self.receiver
            msg['Cc'] = self.cc
            msg.attach(mime_text)

            PURCH_DET_FILE_PATH = os.path.join(CONFIG.CSV_DIR, CONFIG.PURCH_DET_CSV_FILE_NAME)
            COMPLETE_MFG_PATH = os.path.join(CONFIG.CSV_DIR, CONFIG.COMPLETE_MFG_CSV_FILE_NAME)
            
            try:
                with open(PURCH_DET_FILE_PATH, "rb") as attachment:
                    p = MIMEApplication(attachment.read(),_subtype="csv")	
                    p.add_header('Content-Disposition', f"attachment; filename= {CONFIG.PURCH_DET_CSV_FILE_NAME}")
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
                smtp.sendmail(msg['From'], CLIENT+CC , msg.as_string())
                #smtp.send_message(msg)
                print("email Sent")

        except Exception as e:
            raise e
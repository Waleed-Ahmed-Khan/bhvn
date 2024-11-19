
from dotenv import load_dotenv
from common.sqlDBOperations import sqlDBManagement
import os,  datetime, pytz, smtplib
from email.message import EmailMessage
import streamlit as st

load_dotenv()
EMAIL_PASS = os.getenv('EMAIL_PASS')
SENDER = 'donotreply.bhvn.ml@gmail.com'

OLAP_HOST = os.getenv('OLAP_HOST')
OLAP_DB_NAME = os.getenv('OLAP_DB_NAME')
OLAP_USER_NAME = os.getenv('OLAP_USER_NAME')
OLAP_MYSQL_PASS = os.getenv('OLAP_MYSQL_PASS')


class Security:
    def __init__(self, username):
        self.username = username 
        self.password = EMAIL_PASS 
        self.sender = SENDER
        self.datetime = datetime.datetime.now(pytz.timezone("Asia/Jakarta")).strftime("%m/%d/%Y, %H:%M:%S")
        if "mysql_olap_instance" not in st.session_state:
            self.mysql = sqlDBManagement(host = OLAP_HOST,
                                        username = OLAP_USER_NAME,
                                        password = OLAP_MYSQL_PASS,
                                        database = OLAP_DB_NAME)
            st.session_state['mysql_olap_instance'] = self.mysql
        else :
            self.mysql = st.session_state['mysql_olap_instance']
    def pass_change_alert(self):
        try:
            query = f""" SELECT * FROM tblusers WHERE username='{self.username}'"""
            user_data = self.mysql.getDataFramebyQuery(query)
            self.name = user_data['name'][0]
            self.receiver = user_data['email'][0] 
            self.receiver = [self.receiver]
            msg = EmailMessage()
            msg["Subject"] = "Security Alert"
            msg["From"] = self.sender
            msg["To"] = self.receiver

            body = f"""

  Hi {self.name},

  Your password for https://bhvn.ml was changed at {self.datetime} Vietnam Local Time.
  Please take action at https://bhvn.ml if you did not update the password. 
  Or contact admin at hasnain@bhgloves.com ASAP.
  If you're aware of this activity, please disregard this notice. 

  Note: Do not reply to this email as this is a system-generated alert.
  
  Regards,
  BHVN ML
            """
            msg.set_content(body)

            with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
                smtp.starttls()
                smtp.login(self.sender, self.password)
                print("log in successfull!! \nsending email")
                smtp.send_message(msg)
                print("email Sent")
                print(self.name, self.receiver)

        except Exception as e:
            raise e
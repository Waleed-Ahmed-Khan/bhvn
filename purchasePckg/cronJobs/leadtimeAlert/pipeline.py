from extract import Loader
from transform import DataOps
from purchasePckg.cronJobs.leadtimeAlert.mail import Email
from email.mime.text import MIMEText
import os  
import config as CONFIG

class Pipeline:
    def __init__(self, sales_df , purchase_df , customer_po):
        self.sales_df = sales_df.astype({'Completion_pct': int, 'OrderQty': int, 'OutputQty': int})
        self.purchase_df = purchase_df.astype({'Completion_pct': int})
        self.customer_po = customer_po
        self.email = Email()
        self.loader = Loader()

        self.purchase_detail_df = self.loader.get_purchase_detail_df(self.customer_po)
        self.purchase_detail_csv = os.path.join(CONFIG.CSV_DIR, CONFIG.PURCH_DET_CSV_FILE_NAME)
        self.purchase_detail_df.to_excel(self.purchase_detail_csv, index=False)
        
        self.complete_mfg_status = self.loader.get_complete_mfg_status(self.customer_po)
        print(self.complete_mfg_status)
        self.complete_mfg_status[['OrderQty', 'OutputQty']] = self.complete_mfg_status[['OrderQty', 'OutputQty']].fillna(value=0)
        self.complete_mfg_status = self.complete_mfg_status.astype({'Completion_pct': int, 'OrderQty': int, 'OutputQty': int})
        self.complete_mfg_status_styled = self.complete_mfg_status.style.apply(self.highlight_rows, axis = 1)
        self.complete_mfg_status_csv = os.path.join(CONFIG.CSV_DIR, CONFIG.COMPLETE_MFG_CSV_FILE_NAME)
        #self.complete_mfg_status.to_csv(self.complete_mfg_status_csv, index = False)
        self.complete_mfg_status_styled.to_excel(self.complete_mfg_status_csv, index = False)

    def transform(self):
        self.day_remaining = self.sales_df[self.sales_df['CustomerPO'] == self.customer_po]['daysRemaining'].mode(dropna = True)[0]
        self.sale_order_target_date = self.sales_df[self.sales_df['CustomerPO'] == self.customer_po]['Finish'].values[0]
        self.purchase_order_completion = self.purchase_df[self.purchase_df['CustomerPO'] == self.customer_po]['Completion_pct'].values[0]
        if self.day_remaining < 0:
            self.over_due = True
        else: self.over_due = False

    def highlight_rows(self, x):
      if x.Completion_pct == 100:
        return['background-color: green']*10
      elif x.Completion_pct < 100 and x.Completion_pct > 50:
        return['background-color: yellow']*10
      else:
        return['background-color: red']*10

    def send_alert(self):
        if not self.over_due:
            self.subject = f"Heads-up! Pending Purchase alert for {self.customer_po}"
            self.body = f"""

Dear All,

Please take immediate action to make the pending purchase for CustomerPO = {self.customer_po} 
The total days remaining until the order shipment are {self.day_remaining} with the shipment on 

The order detail is as follows:
{self.purchase_df.fillna("N/A").reset_index(drop = True).to_string()}
{self.purchase_df[self.purchase_df["CustomerPO"]==self.customer_po]}

Email alert is generated at {self.email.datetime} Vietnam Local Time.
Note: Do not reply to this email as this is a system-generated alert.

Regards,
BHVN ML
            """
            #self.body = "<h1>Dear ABC</h1>This is the Table <br><br>   "+html_table+"   <br><br> this is image <br><br><img src=ownload.png><br><br>Thanks"
            html = f"""\
        <html>
          <head></head>
          <body>
          <h3>Dear All,</h3>
          Please take the required action to make the pending purchase for <b>Customer PO : {self.customer_po}</b><br>
          The total days remaining until the order shipment are <b>{self.day_remaining}</b> with the shipment on <b>{self.sale_order_target_date}</b><br>
          The current order completion for purchase is <b>{self.purchase_order_completion} %</b> <br>
          The order detail is as follows:
          <h3 align="center">End-to-End Mfg Status</h3> 
            {self.complete_mfg_status.style.set_properties(**{'text-align': 'center'}).to_html(index=False)}
          <h3 align="center">Pending Purchase Detail</h3>
            {self.purchase_detail_df.style.set_properties(**{'text-align': 'center'}).to_html(index=False)}<br><br>
        
          Email alert is generated at <b>{self.email.datetime}</b> Vietnam Local Time.<br>
          <b>Note:</b> Do not reply to this email as this is a system-generated alert.<br><br>

          <b>Regards,</b><br>
          <a href="http://ml.bhgloves.com/"><b>BHVN ML</b></a>
          </body>
        </html>
        """

            mime_text = MIMEText(html, 'html')
        
            self.email.send_alert(self.subject, self.body, mime_text)
        else:
            self.subject = f"Act Now! Purchase overdue alert for {self.customer_po}"
            self.body = f"""

Dear All,

Please take immediate action to make the pending purchase for CustomerPO = {self.customer_po} 
The total days remaining until the order shipment are {self.day_remaining} with the shipment on 

The order detail is as follows:
{self.purchase_df.fillna("N/A").reset_index(drop = True).to_string()}
{self.purchase_df[self.purchase_df["CustomerPO"]==self.customer_po]}

Email alert is generated at {self.email.datetime} Vietnam Local Time.
Note: Do not reply to this email as this is a system-generated alert.

Regards,
BHVN ML
            """
            #self.body = "<h1>Dear ABC</h1>This is the Table <br><br>   "+html_table+"   <br><br> this is image <br><br><img src=ownload.png><br><br>Thanks"
            html = f"""\
        <html>
          <head></head>
          <body>
          <h3>Dear All,</h3>
          Please take immediate action as the purchase for <b>Customer PO : {self.customer_po}</b> is overdue!<br>
          The purchase is overdue by <b>{-(self.day_remaining)} days</b> with the shipment on <b>{self.sale_order_target_date}</b><br>
          The current order completion for purchase is <b>{self.purchase_order_completion} %</b> <br>
          The order detail is as follows:
          <h3 align="center">End-to-End Mfg Status</h3>
            {self.complete_mfg_status.style.set_properties(**{'text-align': 'center'}).to_html(index=False)}
          <h3 align="center">Pending Purchase Detail</h3>
            {self.purchase_detail_df.style.set_properties(**{'text-align': 'center'}).to_html(index=False)}<br><br>
        
          Email alert is generated at <b>{self.email.datetime}</b> Vietnam Local Time.<br>
          <b>Note:</b> Do not reply to this email as this is a system-generated alert.<br><br>

          <b>Regards,</b><br>
          <a href="http://ml.bhgloves.com/"><b>BHVN ML</b></a>
          </body>
        </html>
        """

            mime_text = MIMEText(html, 'html')
        
            self.email.send_alert(self.subject, self.body, mime_text)
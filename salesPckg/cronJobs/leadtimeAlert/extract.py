import os , sys
from pathlib import Path
FILE = Path(__file__).resolve()
ROOT = FILE.parents[2]  # root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative

from common import helper, sqlDBManagement
import config as CONFIG
import pandas as pd
import os,  datetime, pytz
from dotenv import load_dotenv

load_dotenv()

DB_CENT_NAME=os.getenv("DB_CENT_NAME")
DB_CENT_USR=os.getenv("DB_CENT_USR")
DB_CENT_HOST=os.getenv("DB_CENT_HOST")
DB_CENT_PASS=os.getenv("DB_CENT_PASS")

class Loader:
    def __init__(self):
        self.due_threshold_days = CONFIG.DUE_THRESHOLD_DAYS
        self.overdue_threshold_days = CONFIG.OVERDUE_THRESHOLD
        self.olap = sqlDBManagement(host = DB_CENT_HOST, username = DB_CENT_USR,
                    password = DB_CENT_PASS, database = DB_CENT_NAME)

    def get_sales_df (self):

            query = f'''
            SELECT * FROM bhvnbi.mfgcycle 
            WHERE Department IN ('Target')
            AND Completion_pct < 100;
            '''
            self.sales_df = self.olap.getDataFramebyQuery(query)
            self.sales_df['daysRemaining'] = (pd.to_datetime(self.sales_df['Finish']) - pd.to_datetime(datetime.datetime.now(pytz.timezone("Asia/Jakarta")).strftime("%m/%d/%Y, %H:%M:%S"))).dt.days
            self.sales_df = self.sales_df[self.sales_df['daysRemaining'].between(self.overdue_threshold_days, self.due_threshold_days )]
            return self.sales_df
        
    @property
    def pos_sales(self) -> tuple:
        return tuple(self.sales_df['CustomerPO'].unique().tolist())
    
    def get_sales_detail_df(self, customer_po : str) -> pd.DataFrame:
        query = f'''
        SELECT tblarorder.ponumber, tblarorder.id AS SalesOrder, tblarorder.ProductionNo, tblarorderdetail.description, tblitems.size, itemqtyorder,
        lotnumber,tblcustomers.name AS CustomerName, tblarorder.duedate,tblarorder.ex_bhvn_date, tblarorder.bhvnorderentrydate, 
        tblarorder.orderdate
        FROM tblarorderdetail 
        LEFT JOIN  tblarorder ON tblarorder.id = tblarorderdetail.orderid 
        LEFT JOIN tblcustomers ON tblcustomers.customerid = customer_id
        LEFT JOIN tblitems ON tblitems.itemid = tblarorderdetail.itemid
        WHERE ponumber="{customer_po}";
        '''
        return helper.load_data(query)

    def get_complete_mfg_status(self, customer_po):

        query = f'''
        SELECT * FROM bhvnbi.mfgcycle 
        WHERE CustomerPO = "{customer_po}";
        '''
        return self.olap.getDataFramebyQuery(query)
import os , sys
from pathlib import Path
FILE = Path(__file__).resolve()
ROOT = FILE.parents[2]  # root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative

from common import helper, sqlDBManagement
import config as CONFIG
import os,  datetime, pytz
import pandas as pd

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
            SELECT * FROM mfgcycle 
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
        
    @property
    def pos_purchase(self) -> tuple:
        return tuple(self.purchase_df['CustomerPO'].unique().tolist())

    def get_purchase_df (self):
    
        if len(self.pos_sales) == 1:
            po = self.pos_sales[0]
            print(po)
            query = f'''
            SELECT * FROM mfgcycle 
            WHERE Department IN ('Purchase') AND CustomerPO = "{po}"
            AND Completion_pct < 100 ;
            '''
        else:
            query = f'''
            SELECT * FROM mfgcycle 
            WHERE Department IN ('Purchase') AND CustomerPO IN {self.pos_sales}
            AND Completion_pct < 100 ;
            '''
        self.purchase_df = self.olap.getDataFramebyQuery(query)
        return self.purchase_df

    def get_purchase_detail_df(self, customer_po : str) -> pd.DataFrame:
        query = f'''
            SELECT (p.cust_ordno) as cutomer_po, (p.production_ordno) Production_no, (p.ponumber) as purchase_po, (d.itemqty) AS "Order Qty", 
                    insp_det.qtyrcv, insp_det.qty_accepted, insp_det.qty_rejected,
                p.entrydate, p.duedate, tblvendors.vendorname, tblitems.description, d.total, d.net_amount
            FROM tblinvpodetail d
            LEFT JOIN tblmaterialinspection_det insp_det ON d.ponumber = insp_det.ponumber AND d.itemid = insp_det.itemid
            LEFT JOIN tblinvpo p ON d.ponumber = p.ponumber
            LEFT JOIN tblitems ON d.itemid = tblitems.itemid
            LEFT JOIN tblvendors ON p.vendorid = tblvendors.vendorid
            WHERE p.cust_ordno="{customer_po}" 
            AND d.ponumber 
            IN
            (SELECT ponumber FROM tblinvpo WHERE cust_ordno="{customer_po}")
            AND insp_det.qtyrcv IS NULL;
    '''
        df = helper.load_data(query)
        return df

    def get_complete_mfg_status(self, customer_po):

        query = f'''
        SELECT * FROM mfgcycle 
        WHERE CustomerPO = "{customer_po}";
        '''
        return self.olap.getDataFramebyQuery(query)
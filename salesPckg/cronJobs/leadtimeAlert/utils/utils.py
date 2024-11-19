import os , sys
from pathlib import Path
FILE = Path(__file__).resolve()
ROOT = FILE.parents[4]  # root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative

from common import sqlDBManagement
from dotenv import load_dotenv

load_dotenv()
OLTP_MYSQL_PASS=os.getenv("OLTP_MYSQL_PASS")
OLTP_HOST=os.getenv("OLTP_HOST")
OLTP_DB_NAME=os.getenv("OLTP_DB_NAME")
OLTP_USER=os.getenv("OLTP_USER")

oltp = sqlDBManagement(host = OLTP_HOST, username = OLTP_USER,
            password = OLTP_MYSQL_PASS, database = OLTP_DB_NAME)
            
def get_all_pos():
    query = '''SELECT DISTINCT ponumber, mastercode, orderdate, duedate 
              FROM tblarorder;'''

    return oltp.getDataFramebyQuery(query)

def get_qty_done(df_status, total_order_qty):
    import pandas as pd 
    if isinstance(df_status, pd.DataFrame):
        try:
            total_done =  df_status['qty'].sum()
        except KeyError:
            total_done = 0
        pct_complete = round((total_done/total_order_qty)*100, 2)
    else:
        total_done = 0
        pct_complete = 0
    return total_done, pct_complete

def get_status(df):
    if df['OutputQty'] >= df['OrderQty']:
        return "Closed"
    else:
        return "Open"

def get_qty_done(df_status, total_order_qty):
    import pandas as pd 
    if isinstance(df_status, pd.DataFrame):
        try:
            total_done =  df_status['qty'].sum()
        except KeyError:
            total_done = 0
        pct_complete = round((total_done/total_order_qty)*100, 2)
    else:
        total_done = 0
        pct_complete = 0
    return total_done, pct_complete
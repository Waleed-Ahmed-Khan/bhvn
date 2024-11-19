 
from common import helper
import streamlit as st
from datetime import datetime, timedelta 
from common.sqlDBOperations import sqlDBManagement
import appConfig as CONFIG

def get_centos_db():
    if CONFIG.BHVN_CENT_DB_SESSION not in st.session_state:
        st.session_state[CONFIG.BHVN_CENT_DB_SESSION] = sqlDBManagement(host = helper.DB_CENT_HOST, username = helper.DB_CENT_USR,
                            password = helper.DB_CENT_PASS, database = helper.DB_CENT_NAME)
        return st.session_state[CONFIG.BHVN_CENT_DB_SESSION]
    else:
        return st.session_state[CONFIG.BHVN_CENT_DB_SESSION]


def get_all_customer_pos():
    db = get_centos_db()
    query = f'''
        SELECT CustomerPO AS PO, Customer, Start AS Date
        FROM mfgcycle 
        WHERE Department="Target";
    '''
    return db.getDataFramebyQuery(query)

def get_all_mastercodes():
    db = get_centos_db()
    query = f'''
        SELECT MasterCode, Customer
        FROM mfgcycle 
        WHERE Department="Sales";
    '''
    return db.getDataFramebyQuery(query)

def get_so(po_number):
    query = f'''
    SELECT DISTINCT(id) 
    FROM tblarorder 
    WHERE ponumber="{po_number}"
    '''
    return helper.load_data(query)

def get_po_df(po_number):
    db = get_centos_db()
    query = f'''
    SELECT * FROM mfgcycle 
    WHERE CustomerPO="{po_number}"
    '''
    return db.getDataFramebyQuery(query)

def get_strategic_df(customer_name, mastercode):
    customer_name = tuple(customer_name)
    mastercode = tuple(mastercode)
    db = get_centos_db()
    query = f'''
    SELECT * FROM mfgcycle 
    WHERE Customer IN {customer_name}
    AND MasterCode IN {mastercode}
    AND Department != "Target"
    '''
    return db.getDataFramebyQuery(query)

def get_item(po_number):
    query = f'''
            SELECT DISTINCT(tblarorderdetail.description)
            FROM tblarorderdetail 
            LEFT JOIN  tblarorder ON tblarorder.id = tblarorderdetail.orderid 
            WHERE ponumber="{po_number}"
    '''
    return helper.load_data(query)
    
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

def get_customers(po_datetime_selection):
    db = get_centos_db()
    query = f'''
        SELECT DISTINCT(Customer) AS Customer FROM mfgcycle
        WHERE Start >= "{po_datetime_selection}";
    '''
    return db.getDataFramebyQuery(query)

def get_po_selection_date(po_time_selection):
    if po_time_selection == "Last Week POs":
        po_time_selection = datetime.today() - timedelta(days=7)
    elif po_time_selection == "Last One Month POs":
        po_time_selection = datetime.today() - timedelta(days=30)
    elif po_time_selection == "Last Six Month POs":
        po_time_selection = datetime.today() - timedelta(days=183)
    elif po_time_selection == "Last One Year POs":
        po_time_selection = datetime.today() - timedelta(days=365)
    elif po_time_selection == "All POs from beginning":
        po_time_selection = '2013-01-01'
    return po_time_selection
def get_dep_status_vars(df, purchase = False):
    if purchase:
        min_date = df['Order Date'].min()
        max_date = df['Received Date'].max()
    else:
        min_date = df['date'].min()
        max_date = df['date'].max()
    leadtime = max_date - min_date
    try:
        leadtime = leadtime.days
    except AttributeError:
        leadtime = 0
    return min_date.strftime('%d %b, %Y'), max_date.strftime('%d %b, %Y'), leadtime

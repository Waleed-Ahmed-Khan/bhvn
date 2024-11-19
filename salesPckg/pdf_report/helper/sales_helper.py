
import pandas as pd 
import numpy as np 
import os
from dotenv import load_dotenv
import mysql.connector as sql

load_dotenv()

OLTP_MYSQL_PASS = os.getenv('OLTP_MYSQL_PASS')
SQL_DWH_PASS = os.getenv("OLAP_MYSQL_PASS")
COSMOS_CONN_STR = os.getenv("COSMOS_CONN_STR")
OLAP_HOST = os.getenv("OLAP_HOST")
OLAP_DB_NAME = os.getenv("OLAP_DB_NAME")
OLAP_USER_NAME = os.getenv("OLAP_USER_NAME")

def load_data(query):
    mydb = sql.connect( 
    host = "bhvnerp.com",
    user = 'bhvnerp_hasnain',
    passwd = OLTP_MYSQL_PASS,
    database = 'bhvnerp_bhv2019')
    df = pd.read_sql_query(query, mydb)
    return df

def load_sales_invoice_data():
    query = '''
    SELECT det.customer_ponumber,inv.bhvnpo, inv.custumInvoiceNo, det.invoiceid, inv.invoicedate, inv.shipdate,
        inv.booking_pdate,inv.booking_rdate, inv.shipcost,inv.AdvancePayment, inv.freight,
        inv.cosignee, inv.cosig_address, inv.brand, inv.bankname, inv.container, 
        inv.vesseldate, inv.vesselno, det.itemid, det.itemdescription, det.priceach, det.qty, 
        det.amount, det.discountPercent, det.exchange_rate, det.price_InCurrency,det.lotnumber, det.Cartons, 
        det.modelcode, det.hscode, det.imancode, det.container
    FROM tblinvoice inv
    LEFT JOIN tblinvoicedetail det ON
        det.invoiceid = inv.invoicenumber;
    '''
    inv = helper.load_data(query=query)
    inv.rename(columns = {'customer_ponumber':'custponumber'}, inplace =True)
    inv = inv[inv['custponumber'] !='']
    query = '''
    SELECT tblarorder.ponumber, tblarorder.id AS SalesOrder, tblarorder.ProductionNo, tblarorderdetail.description, 
		   tblarorderdetail.itemid, tblitems.size, itemqtyorder, tblarorder.shipTo_comp_name AS custname, lotnumber, tblarorder.confirmdate,
           tblarorder.duedate,tblarorder.ex_bhvn_date, tblarorder.bhvnorderentrydate, tblarorder.orderdate
    FROM tblarorderdetail 
    LEFT JOIN  tblarorder ON 
           tblarorder.id = tblarorderdetail.orderid 
    LEFT JOIN tblitems ON
           tblitems.itemid = tblarorderdetail.itemid
    '''
    order = helper.load_data(query=query)
    complete_sales = pd.merge(inv, order, how = 'left',
                             left_on=['custponumber', 'itemid'],
                             right_on = ['ponumber', 'itemid']
                             )
    #complete_sales = complete_sales.astype({'invoicedate': "datetime64[ns]" , 'shipdate': "datetime64[ns]"})
    #complete_sales['pomonth_number'] = pd.to_datetime(complete_sales['orderdate'])
    time_stamp = ['invoicedate', 'shipdate', 'orderdate', 'confirmdate', 'duedate', 'ex_bhvn_date', 'bhvnorderentrydate', 'booking_rdate','booking_pdate']
    for col in time_stamp:
        complete_sales[col] = [pd.to_datetime(x, infer_datetime_format=True) if pd.notnull(x) else x for x in complete_sales[col]]
    
    non_time_stamp = [col for col in complete_sales.columns if col not in time_stamp]
    for col in non_time_stamp:
        complete_sales[col] = [np.nan if pd.isnull(x) or len(str(x))<1 else x for x in complete_sales[col]]
    complete_sales.rename(columns = {'qty': 'shipped_qty', 'itemqtyorder':'order_qty', 'price_InCurrency':'Price(USD)'}, inplace=True)
    
    complete_sales['pomonth_number'] = complete_sales['orderdate'].dt.month
    complete_sales['salesmonth_number'] = complete_sales['invoicedate'].dt.month
    complete_sales['Year'] = complete_sales['invoicedate'].dt.year.astype(int)
    complete_sales['pomonth'] = complete_sales['orderdate'].dt.month_name().str.slice(stop=3)
    complete_sales['salesmonth'] = complete_sales['invoicedate'].dt.month_name().str.slice(stop=3)
    complete_sales['target_lead_time'] = (complete_sales['duedate'] - complete_sales['orderdate']).dt.days
    complete_sales['actual_lead_time'] = np.where(((complete_sales['shipdate'].isnull()) | (complete_sales['orderdate'].isnull())), 0, (complete_sales['shipdate'] - complete_sales['orderdate']).dt.days) 
    complete_sales['delay_days'] = complete_sales['actual_lead_time'] - complete_sales['target_lead_time']
    complete_sales['booking_conf_time'] = np.where((complete_sales['booking_rdate'].isnull()) | (complete_sales['booking_pdate'].isnull()), 0,  (complete_sales['booking_rdate'] - complete_sales['booking_pdate']).dt.days)
    complete_sales['Delayed Qty'] = np.where(complete_sales['delay_days'] <= 0, 0 , complete_sales['shipped_qty'])
    complete_sales['percent_qty_delayed'] = (complete_sales['Delayed Qty']/complete_sales['shipped_qty'])*100
    complete_sales['HOT'] =  ((complete_sales['shipped_qty'] - complete_sales['Delayed Qty']) / complete_sales['shipped_qty']) *100
    
    return complete_sales
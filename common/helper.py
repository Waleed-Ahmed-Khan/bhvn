import streamlit as st
import mysql.connector as sql
import pandas as pd 
import sqlite3, hashlib, calendar, os
import numpy as np
from datetime import datetime
from dotenv import load_dotenv
import sqlalchemy
from common.sqlDBOperations import sqlDBManagement

import pandas as pd
import streamlit as st
from io import BytesIO
from st_aggrid import AgGrid
import appConfig as CONFIG

def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    format1 = workbook.add_format({'num_format': '0.00'}) 
    worksheet.set_column('A:A', None, format1)  
    writer.save()
    return output
    

load_dotenv()

OLTP_MYSQL_PASS = os.getenv('OLTP_MYSQL_PASS')
SQL_DWH_PASS = os.getenv("OLAP_MYSQL_PASS")
COSMOS_CONN_STR = os.getenv("COSMOS_CONN_STR")
OLAP_HOST = os.getenv("OLAP_HOST")
OLAP_DB_NAME = os.getenv("OLAP_DB_NAME")
OLAP_USER_NAME = os.getenv("OLAP_USER_NAME")

DB_CENT_NAME=os.getenv("DB_CENT_NAME")
DB_CENT_USR=os.getenv("DB_CENT_USR")
DB_CENT_HOST=os.getenv("DB_CENT_HOST")
DB_CENT_PASS=os.getenv("DB_CENT_PASS")

def get_db_engine(username, user_pass, server, db):
    url = f"mysql+pymysql://{username}:{user_pass}@{server}:3306/{db}"
    engine = sqlalchemy.create_engine(url)
    return engine

@st.cache(suppress_st_warning=True, allow_output_mutation=True, show_spinner =False, ttl=800)
def load_data(query):
    mydb = sql.connect( 
    host = "bhvnerp.com",
    user = 'bhvnerp_hasnain',
    passwd = OLTP_MYSQL_PASS,
    database = 'bhvnerp_bhv2019')
    df = pd.read_sql_query(query, mydb)
    return df

def connect_sql_olap():
    cxn = sql.connect(user=DB_CENT_USR, password=DB_CENT_PASS, host=DB_CENT_HOST, port=3306, database=DB_CENT_NAME)
    cursor=cxn.cursor()
    return cursor, cxn

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False

# conn = sqlite3.connect('users.db', check_same_thread=False)
# c = conn.cursor()

############################### ipTable ##############################################################
# def create_ipTable():
#     c.execute('''CREATE TABLE IF NOT EXISTS ipTable(IP TEXT NOT NULL,
#                  City TEXT, Region Text, CountryCode Text, Location TEXT,
#                  Organization TEXT, PostalCode INT, TimeZone TEXT, CountryName TEXT, 
#                  Latitude FLOAT, Longitude FLOAT,
#                 PRIMARY KEY(IP))''')
#     conn.commit()
# def get_all_ips_data():
#     all_ips = c.execute("SELECT * FROM ipTable")
#     all_ips = pd.DataFrame(all_ips, columns=['IP', 'City', 'Region', 'CountryCode', 'Location','Organization', 'PostalCode', 'TimeZone', 'CountryName', 'Latitude', 'Longitude' ])
#     st.dataframe(all_ips)
#     return all_ips
# def add_new_ip(userip, City, Region, CountryCode, Location,Organization, PostalCode, TimeZone, CountryName, Latitude, Longitude):
#     create_ipTable()
#     all_ips = get_all_ips_data()
#     if userip not in list(all_ips['IP']):
#         c.execute('''
#                     INSERT INTO ipTable
#                     (IP,City, Region, CountryCode, Location,
#                     Organization, PostalCode, TimeZone, CountryName, Latitude, Longitude) VALUES (?,?,?,?,?,?,?,?,?,?,?)
#                     ''', (userip, City, Region, CountryCode, Location,Organization, PostalCode, TimeZone, CountryName, Latitude, Longitude)
#                     )
#         conn.commit()

######################################## userlogsTable ################################################################
# def create_userlogsTable():
#     cursor_oracle_db.execute('''CREATE TABLE IF NOT EXISTS userlogsTable(username TEXT NOT NULL, DateTimeLocal DATETIME, DateTimeUTC DATETIME,
#             IP TEXT , Activity TEXT,FOREIGN KEY (IP) REFERENCES ipTable(IP),
#             PRIMARY KEY (username, DateTimeLocal));
#             ''')
#     conn_oracle_db.commit()    
def add_userLogs(username, datetimelocal, datetimeutc, activity):
    #create_userlogsTable()
    if CONFIG.BHVN_CENT_DB_SESSION not in st.session_state:
        st.session_state[CONFIG.BHVN_CENT_DB_SESSION] = sqlDBManagement(host = DB_CENT_HOST, username = DB_CENT_USR,
                            password = DB_CENT_PASS, database = DB_CENT_NAME)
    query = f'''INSERT INTO userlogs(UserName, DateTimeVN, DateTimeUTC, Activity)
                VALUES ("{username}","{datetimelocal}", "{datetimeutc}","{activity}")'''
    st.session_state[CONFIG.BHVN_CENT_DB_SESSION].executeOperation(query=query)
    #cursor_sql_olap , conn_sql_olap = connect_sql_olap()
    #sql = ('INSERT INTO userlogs(UserName, DateTimeVN, DateTimeUTC, Activity) values (%s, %s, %s, %s)')
    #cursor_sql_olap.execute(sql, [username, datetimelocal, datetimeutc, activity])
    #conn_sql_olap.commit()

def get_user_logs(user_logs):
    #user_logs = cursor.execute("SELECT * FROM USERLOGS")
    #conn.commit()
    #user_logs = db_session.getDataFramebyQuery("SELECT * FROM userlogs;")
    #user_logs = pd.read_sql_query("SELECT * FROM userlogs", conn)
    #AgGrid(userss)
    #st.write("inside get user logs", user_logs)
    #user_logs = pd.DataFrame(user_logs, columns=['UserName', 'DateTimeVN', 'DateTimeUTC', 'Activity'])
    #st.write("stage 2-----------------")  
    user_logs['DateTimeVN'] = pd.to_datetime(user_logs['DateTimeVN'], utc=False)
    user_logs['DateTimeUTC'] = pd.to_datetime(user_logs['DateTimeUTC'], utc=True)
    user_logs['DateTimeUTC'] = user_logs['DateTimeUTC'].dt.strftime("%Y/%m/%d, %H:%M:%S") 
    
    #user_logs['DateTimeUTC'] = [x.strftime("%m/%d/%Y, %H:%M:%S") for x in pd.to_datetime(user_logs['DateTimeUTC'])]
    #user_logs['DateTimeLocal'] = [x.strftime("%m/%d/%Y, %H:%M:%S") for x in pd.to_datetime(user_logs['DateTimeLocal'])]
    user_logs['Month Number'] = pd.to_datetime(user_logs['DateTimeUTC']).dt.month
    user_logs['Month'] = pd.to_datetime(user_logs['DateTimeUTC']).dt.strftime("%b")
    user_logs['Day Number'] = pd.to_datetime(user_logs['DateTimeUTC']).dt.day
    user_logs['Day'] = pd.to_datetime(user_logs['DateTimeUTC']).dt.strftime("%a")
    user_logs['activity_count'] = 1
    return user_logs

################################# usertable ###################################################################################

# def create_usertable():
#     c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT NOT NULL, password TEXT, rights TEXT, PRIMARY KEY(username))')
#     conn.commit()
# def add_userdata(username, password, rights):
#     c.execute('INSERT INTO userstable(username,password, rights) VALUES (?,?,?)',
#     (username, password, rights))
#     conn.commit()
# def update_user_pass_helper(username, password):
#     c.execute('UPDATE userstable SET password =? WHERE username =?',(password, username))
#     conn.commit()
#     st.success(f'Password for username "{str.title(username)}" has been updated successfully, please login using the updated password, Thank you! 😊')
# def login_user(username, password):
#     c.execute('SELECT * FROM userstable WHERE username =? AND password = ?',
#                 (username, password))
#     data = c.fetchall()
#     return data

# def view_all_users():
#     c.execute('SELECT * FROM  userstable')
#     data = c.fetchall()
#     return data 

# def del_user_helper(username):
#     c.execute('DELETE FROM userstable WHERE username = ?',(username,))
#     conn.commit()
#     st.info(f'{username} has been deleted successfully')
# ########################## allRights #########################################################################################
# def create_allRights():
#     c.execute('CREATE TABLE IF NOT EXISTS allRights(rights TEXT NOT NULL, "order" TEXT,  PRIMARY KEY(rights))')
#     #c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT NOT NULL, password TEXT, rights TEXT, PRIMARY KEY(username))')
#     conn.commit()
# def add_new_rights(rights, order):
#     c.execute('INSERT INTO allRights(rights, "order") VALUES (?,?)',(rights, order))
#     conn.commit()
# def get_all_rights():
#     c.execute("SELECT * FROM allRights")
#     data = c.fetchall()
#     df_rights = pd.DataFrame(data, columns=['Rights', 'Order'])
#     df_rights = df_rights.sort_values(by='Order', ascending=True)
#     return df_rights
# def update_rights_table(rights, order):
#     c.execute('UPDATE allRights SET "order" =? WHERE rights =?',(order, rights))
#     conn.commit()
# def delete_rights_helper(rights):
#     c.execute('DELETE FROM allRights WHERE rights =?',(rights,))
#     conn.commit()
# def update_rights_helper(username, rights):
#     rights = ','.join([i for i in  rights])
#     c.execute('UPDATE userstable SET rights =? WHERE username =?',(rights, username))
#     conn.commit()
#     st.success(f'User Rights for "{username}" has been updated successfully')


def get_month_number(x):
    if x == 'Jan':
        x = 1
    elif x == 'Feb':
        x = 2
    elif x == 'Mar':
        x = 3
    elif x == 'Apr':
        x = 4 
    elif x == 'May':
        x = 5
    elif x == 'Jun':
        x = 6
    elif x == 'Jul':
        x = 7
    elif x == 'Aug':
        x = 8
    elif x == 'Sep':
        x = 9
    elif x == 'Oct':
        x = 10
    elif x == 'Nov':
        x = 11
    elif x == 'Dec':
        x = 12
    return x
#@st.cache(suppress_st_warning=True, allow_output_mutation=True, ttl = 150)
def preprocess_purch(purch, start_date, end_date , purch_ord_status, po_selection, year, customer_po_selection, vendor_selection, categories_selection, source ):
    mask = (purch['Order Date'].astype('datetime64').dt.date.between(start_date, end_date)) & (purch['Order Status'].isin(purch_ord_status)) & (purch['Purchase Order #'].isin(po_selection)) & (purch['year']==year) & (purch['Customer PO'].isin(customer_po_selection)) & (purch['Vendor Name'].isin(vendor_selection)) & (purch['Category'].isin(categories_selection)) & (purch['source'].isin(source))
    purch = purch[mask]
    purch['Required Date'] = pd.to_datetime(purch['Required Date'])
    purch['Order Date'] = pd.to_datetime(purch['Order Date'])
    purch['Received Date'] = pd.to_datetime(purch['Received Date']) 
    purch['month_num'] = purch['Order Date'].dt.month
    purch['Month'] = purch['month_num'].apply(lambda x: calendar.month_abbr[x])
    purch['Lead Time (Days)'] = purch['Received Date'] - purch['Order Date']
    purch['lead_time_req'] = (purch['Required Date'] -  purch['Order Date']).dt.days
    purch['Lead Time (Days)'] = purch['Lead Time (Days)'] / pd.Timedelta(1, unit='d')
    purch["%age DR"] = purch['Rejected Qty'] / purch['Ordered Qty']
    purch['delivery score'] = purch['Delay (Days)'].apply(lambda x: 0 if x > 0 else 5)
    purch.loc[purch['Delay (Days)'].isnull(), "delivery score"] = np.nan 
    purch['quality score'] = purch['%age DR'].apply(lambda x: 5 if x == 0 else 0)
    purch.loc[purch['Delay (Days)'].isnull(), "quality score"] = np.nan 
    purch['Vendor Score'] = (purch['delivery score'] + purch['quality score']) / 2
    purch['Category'] = purch['Category'].map({'Accessories':'Accessories', '':'Accessories', 'Packing': 'Packing', 'Processing':'Processing', 'Fabric':'Fabric'})
    #purch['Nature'] = purch['Nature'].map({'Major':'Major','Minor':'Minor', 'Critical':'Critical','':'Major'})
    purch['ontime_qty'] = np.where(purch['Ontime/Delay'] == 'Ontime', purch['Received Qty'], np.nan)
    delay = purch[['Purchase Order #', 'Delay (Days)', 'Month', 'month_num']][purch['Delay (Days)']>0]
    delay = delay.groupby(['Purchase Order #','Month']).mean().reset_index()

    delay = delay[delay['Delay (Days)'].notnull()].sort_values('month_num', ascending = True)
    delay = delay[['Month', 'Delay (Days)', 'month_num']].groupby( 'Month', as_index = False).agg(
        Delay_Days = pd.NamedAgg('Delay (Days)', aggfunc='mean'),
        month_num = pd.NamedAgg('month_num', aggfunc='max')
    ).sort_values('month_num', ascending = True)
    delay = delay.rename(columns={'Delay_Days': 'Delay (Days)'})

    if isinstance(delay, pd.DataFrame):
        try:
            Avg_Delay = int(round(delay['Delay (Days)'].mean(), 0))
        except ValueError:
            Avg_Delay = round(delay['Delay (Days)'].mean(), 0)

        lead_t = purch[['Lead Time (Days)', 'lead_time_req', 'Month', 'month_num']].groupby('Month', as_index= False).agg(
                    LeadTime = pd.NamedAgg('Lead Time (Days)', aggfunc='mean'),
                    LeadTimeReq = pd.NamedAgg('lead_time_req', aggfunc='mean'),
                    month_num = pd.NamedAgg('month_num', aggfunc='max')
        ).sort_values('month_num', ascending = True)

        lead_t = lead_t.rename(columns = {'LeadTime':'Lead Time (Days)', 'LeadTimeReq':'Target Lead Time (Days)'})

        #lead_t = purch[['Purchase Order #', 'Lead Time (Days)', 'Month', 'month_num']].groupby(['Purchase Order #','Month']).mean().reset_index()
        #lead_t = lead_t[lead_t['Lead Time (Days)'].notnull()].sort_values('month_num', ascending = True)
        #lead_t = lead_t[['Purchase Order #','Month', 'Lead Time (Days)', 'month_num']].groupby('Month').mean().reset_index().sort_values('month_num', ascending = True)
        Avg_lead_time = int(round(lead_t['Lead Time (Days)'].mean(),2))

        purch_delayed = purch[purch['Ontime/Delay'] == 'Delayed']
        #prc_delay = purch_delayed[['Purchase Order #', 'Ontime/Delay', 'Month', 'month_num']].groupby(['Purchase Order #', 'Month'], as_index= False).agg('count')
        prc_delay = purch_delayed[['Ontime/Delay', 'Month', 'month_num']].groupby('Month', as_index= False).agg(
                    OntimeDelay = pd.NamedAgg('Ontime/Delay', aggfunc='count'),
                    month_num = pd.NamedAgg('month_num', aggfunc='max')
        )
        prc_delay = prc_delay.rename(columns={'Month':'Month_del', 'OntimeDelay':'Delayed_orders'})

        closed = purch[(purch['Ontime/Delay'].notnull()) & (purch['Received Qty'] >= purch['Ordered Qty'])]

        closed = closed[['Ontime/Delay', 'Month', 'month_num']].groupby('Month', as_index= False).agg(
                    OntimeDelay = pd.NamedAgg('Ontime/Delay', aggfunc='count'))
        closed = closed.rename(columns = {'OntimeDelay': 'Ontime/Delay'})
        combined_prc_del =  pd.merge(prc_delay[['Month_del','Delayed_orders', 'month_num']],
                                    closed[['Month', 'Ontime/Delay']], how='right', left_on='Month_del',
                                    right_on='Month').sort_values('month_num', ascending=True)
        combined_prc_del['Percent Delay'] = (combined_prc_del['Delayed_orders']/combined_prc_del['Ontime/Delay'])*100
        combined_prc_del = combined_prc_del.fillna(0)
        Percent_Delays = sum(combined_prc_del['Percent Delay'])/purch['Month'].nunique()
        Percent_Delays = round(Percent_Delays,0)


        filtered_purch = purch.copy()
        # Calculate total orders, ontime orders, and percent ontime
        total_orders = len(filtered_purch)  # Total number of orders
        ontime_orders = (filtered_purch['Ontime/Delay'] == 'Ontime').sum()  # Count of ontime orders
        percent_ontime = (ontime_orders / total_orders) * 100 if total_orders > 0 else 0  # Percentage ontime
        
        ontime_data = purch.groupby('Month', as_index=False).agg(
        TotalOrders=pd.NamedAgg(column='Purchase Order #', aggfunc='count'),
        OntimeOrders=pd.NamedAgg(column='Ontime/Delay', aggfunc=lambda x: (x == 'Ontime').sum()),
        month_num=pd.NamedAgg(column='month_num', aggfunc='max'))
        ontime_data['% On-Time'] = (ontime_data['OntimeOrders'] / ontime_data['TotalOrders']) * 100
        ontime_data = ontime_data.sort_values('month_num')


        Total_Delayed_Orders =  sum(combined_prc_del['Delayed_orders'])
        Total_Placed_Orders = sum(combined_prc_del['Ontime/Delay'])
        data_for_facet = purch.groupby(by = ['Month', 'Ontime/Delay', 'Category', 'Nature'], as_index=True).mean()[['Lead Time (Days)']].reset_index()
        current_date = datetime.today().strftime('%Y-%m-%d')
        current_date = pd.to_datetime(current_date)
        purch['Days Remaining'] =  np.where(pd.isnull(purch['Received Date']), (purch['Required Date'] - current_date)/pd.Timedelta(1, unit='d'), np.nan)
        open_orders = purch[(purch['Received Date'].isnull()) & (purch['Vendor Name'] != 'IMPORTS')]     
        avg_remaining_days = open_orders[['Purchase Order #', 'Days Remaining']].groupby('Purchase Order #').mean().reset_index()
        avg_remaining_days = avg_remaining_days.groupby('Purchase Order #').mean().reset_index().sort_values('Days Remaining', ascending = True)
        avg_remaining_days = avg_remaining_days.sort_values('Days Remaining', ascending= False)
        #purch = purch.drop(columns=['Received Qty'])
        percent_dr_vendor_score_df = purch[purch['Received Date'].notnull()]
        percent_dr_vendor_score_df = percent_dr_vendor_score_df.groupby('Month').mean().reset_index().sort_values('month_num')[['Month', 'Vendor Score', '%age DR']]
        avg_vendor_score = percent_dr_vendor_score_df['Vendor Score'].mean()
        avg_percent_dr = percent_dr_vendor_score_df['%age DR'].mean()

        hot_df = purch[['Month', 'Received Qty', 'ontime_qty', 'month_num']].groupby('Month', as_index = False).agg(
            ReceivedQty = pd.NamedAgg('Received Qty', aggfunc='sum'),
            OntimeQty = pd.NamedAgg('ontime_qty', aggfunc='sum'),
            month_num = pd.NamedAgg('month_num', aggfunc='max')
                    ).sort_values('month_num', ascending = True)
        hot_df['% HOT'] = round((hot_df['OntimeQty'])/hot_df['ReceivedQty'] * 100, 1)
        return purch ,delay , Percent_Delays, percent_ontime, ontime_data, combined_prc_del, Avg_Delay, lead_t, Avg_lead_time, Total_Delayed_Orders, avg_remaining_days, Total_Placed_Orders, percent_dr_vendor_score_df, avg_percent_dr, avg_vendor_score, data_for_facet, hot_df
    else :
        return 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
@st.cache(suppress_st_warning=True, allow_output_mutation=True, ttl = 150)
def preprocess_cutting(cutting_qc, cutting_df, date_selection, po_selection, opr_selection):
    mask_qc = (cutting_qc['date'].between(*date_selection)) & (cutting_qc['Customer_PO'].isin(po_selection)) & (cutting_qc['opr_code'].isin(opr_selection))
    mask_cutting_df = (cutting_df['date'].between(*date_selection)) & (cutting_df['customer_PO'].isin(po_selection)) & (cutting_df['opr_code'].isin(opr_selection))
    
    cutting_qc = cutting_qc[mask_qc]
    cutting_df = cutting_df[mask_cutting_df]

    if ((isinstance (cutting_qc, pd.DataFrame)) & (isinstance (cutting_df, pd.DataFrame))) :
        pie_bar_defect_type_qc = cutting_qc[['defect_type', 'defectQty']]
        pie_bar_defect_type_qc = pie_bar_defect_type_qc.groupby(by='defect_type').sum().reset_index().sort_values(by='defectQty', ascending= True)
        pie_bar_opr_code_qc = cutting_qc[['opr_code', 'defectQty']]
        pie_bar_opr_code_qc = pie_bar_opr_code_qc.groupby(by='opr_code').sum().reset_index().sort_values(by='defectQty', ascending= True)
        return pie_bar_defect_type_qc, pie_bar_opr_code_qc, cutting_df
    else :
        return 0, 0, 0




@st.cache(suppress_st_warning=True, allow_output_mutation=True, ttl = 150)
def preprocess_sewing(complete_df, start_date, end_date, year, po_selection, customer_selection, line_selection, mastercode_selection, size_selection):
    
    mask =  (complete_df['date'].astype('datetime64').dt.date.between(start_date, end_date)) & (complete_df['year'] == year) & (complete_df['customer_PO'].isin(po_selection)) & (complete_df['SubCategory'].isin(customer_selection)) & (complete_df['line_number'].isin(line_selection)) & (complete_df['mastercode'].isin(mastercode_selection)) & (complete_df['size'].isin(size_selection))
    complete_df = complete_df[mask]
    complete_df = complete_df.dropna(subset = ['mastercode', 'size']) #adding mastercode == nan will increase the number of co

    #targets = complete_df['h_target'].values
    complete_df["h_target"] = complete_df["h_target"].apply(lambda x : 50 if x == 0 else x) 
    #complete_df = complete_df[pd.notna(complete_df['mastercode'])]
    total_output = complete_df['qty'].sum()
    total_target = complete_df['target'].sum()
    total_co = complete_df['C/O'].sum()
    
    total_percent_co = (total_co/len(complete_df['C/O']))*100
    avg_efficiency = (complete_df["% Eff"].mean())*100
    avg_throughput = complete_df['Hourly Throughput'].mean()
    complete_df["% Eff"]  = (complete_df['% Eff'])*100

    sorted_months = complete_df.groupby(by='Month', as_index=False)['month_no'].first()
    
    co_by_month = complete_df.groupby(by='Month', as_index=False)['C/O'].sum()
    executions_by_month = complete_df.groupby(by='Month', as_index=False)['C/O'].count().rename(columns={'C/O':'count_co'})
    co_exe_by_month = pd.merge(left=co_by_month, right=executions_by_month, on='Month', how='left')
    co_exe_by_month['percent_co'] = (co_exe_by_month['C/O']/co_exe_by_month['count_co'])*100
    co_exe_by_month = co_exe_by_month.drop(columns=['C/O', 'count_co'])
    co_exe_by_month = pd.merge(left=co_exe_by_month, right=sorted_months, how='left').sort_values(by='month_no', ascending= True).drop(columns=['month_no'])
    eff_by_month = complete_df.groupby(by='Month', as_index=False)['% Eff'].mean()
    eff_by_month = pd.merge(left=eff_by_month, right=sorted_months, how='left').sort_values(by='month_no', ascending=True).drop(columns=['month_no'])
    eff_by_month['% Eff'] = eff_by_month['% Eff']
    throughput_by_month = complete_df.groupby(by='Month', as_index=False)['Hourly Throughput'].mean()
    throughput_by_month = pd.merge(left=throughput_by_month, right=sorted_months, how='left').sort_values(by='month_no', ascending=True).drop(columns=['month_no'])
    
    customer_wise_throughput = complete_df.groupby('SubCategory', as_index=False)['Hourly Throughput'].mean()
    customer_wise_eff = complete_df.groupby('SubCategory', as_index=False)['% Eff'].mean()
    customer_wise_eff_thr = pd.merge(left=customer_wise_throughput, right=customer_wise_eff, how='left').sort_values(by='% Eff', ascending = False)
    line_wise_throughput = complete_df.groupby('line_number', as_index=False)['Hourly Throughput'].mean()
    line_wise_eff = complete_df.groupby('line_number', as_index=False)['% Eff'].mean()
    line_wise_eff_thr = pd.merge(left=line_wise_throughput, right=line_wise_eff, how='left').sort_values(by='% Eff', ascending = False)
    
    customer_qty = complete_df.groupby(by='SubCategory', as_index=False)['qty'].sum().rename(columns={'SubCategory':'Customer Name', 'qty': 'Quantity'})
    
    co_by_brand = complete_df.groupby(by='SubCategory', as_index=False)['C/O'].sum()
    co_by_line = complete_df.groupby(by='line_number', as_index=False)['C/O'].sum()
    return complete_df, total_output, total_target, total_co, total_percent_co, avg_efficiency, avg_throughput , sorted_months, co_exe_by_month,eff_by_month, throughput_by_month, customer_wise_eff_thr, line_wise_eff_thr, customer_qty, co_by_brand, co_by_line

@st.cache(suppress_st_warning=True, allow_output_mutation=True, ttl = 150)
def preprocess_sewing_lastworking(complete_df):
    total_output = complete_df['qty'].sum()
    total_target = complete_df['target'].sum()
    total_co = complete_df['C/O'].sum()
    
    total_percent_co = (total_co/len(complete_df['C/O']))*100
    avg_efficiency = (complete_df["% Eff"].mean())*100
    avg_throughput = complete_df['Hourly Throughput'].mean()
    complete_df["% Eff"]  = (complete_df['% Eff'])*100

    sorted_months = complete_df.groupby(by='Month', as_index=False)['month_no'].first()
    
    co_by_month = complete_df.groupby(by='Month', as_index=False)['C/O'].sum()
    executions_by_month = complete_df.groupby(by='Month', as_index=False)['C/O'].count().rename(columns={'C/O':'count_co'})
    co_exe_by_month = pd.merge(left=co_by_month, right=executions_by_month, on='Month', how='left')
    co_exe_by_month['percent_co'] = (co_exe_by_month['C/O']/co_exe_by_month['count_co'])*100
    co_exe_by_month = co_exe_by_month.drop(columns=['C/O', 'count_co'])
    co_exe_by_month = pd.merge(left=co_exe_by_month, right=sorted_months, how='left').sort_values(by='month_no', ascending= True).drop(columns=['month_no'])
    eff_by_month = complete_df.groupby(by='Month', as_index=False)['% Eff'].mean()
    eff_by_month = pd.merge(left=eff_by_month, right=sorted_months, how='left').sort_values(by='month_no', ascending=True).drop(columns=['month_no'])
    eff_by_month['% Eff'] = eff_by_month['% Eff'] *100
    throughput_by_month = complete_df.groupby(by='Month', as_index=False)['Hourly Throughput'].mean()
    throughput_by_month = pd.merge(left=throughput_by_month, right=sorted_months, how='left').sort_values(by='month_no', ascending=True).drop(columns=['month_no'])
    
    customer_wise_throughput = complete_df.groupby('SubCategory', as_index=False)['Hourly Throughput'].mean()
    customer_wise_eff = complete_df.groupby('SubCategory', as_index=False)['% Eff'].mean()
    customer_wise_eff_thr = pd.merge(left=customer_wise_throughput, right=customer_wise_eff, how='left').sort_values(by='% Eff', ascending = False)
    line_wise_throughput = complete_df.groupby('line_number', as_index=False)['Hourly Throughput'].mean()
    line_wise_eff = complete_df.groupby('line_number', as_index=False)['% Eff'].mean()
    line_wise_eff_thr = pd.merge(left=line_wise_throughput, right=line_wise_eff, how='left').sort_values(by='% Eff', ascending = False)
    
    customer_qty = complete_df.groupby(by='SubCategory', as_index=False)['qty'].sum().rename(columns={'SubCategory':'Customer Name', 'qty': 'Quantity'})
    
    co_by_brand = complete_df.groupby(by='SubCategory', as_index=False)['C/O'].sum()
    co_by_line = complete_df.groupby(by='line_number', as_index=False)['C/O'].sum()
    co_by_line = co_by_line[co_by_line['C/O'] != 0]

    planned_vs_target = complete_df.groupby('line_number', as_index=False)[['qty','target']].sum().rename(columns={'qty':'Output', 'target':'Target'}).astype({'Output':int, 'Target': int})
    
    return complete_df, total_output, total_target, total_co, total_percent_co, avg_efficiency, avg_throughput , sorted_months, executions_by_month ,eff_by_month, throughput_by_month, customer_wise_eff_thr, line_wise_eff_thr, customer_qty, co_by_brand, co_by_line, planned_vs_target

@st.cache(suppress_st_warning=True, allow_output_mutation=True, ttl = 150)
def preprocess_auto(complete_df, start_date, end_date, year, po_selection, customer_selection, opr_selection, mastercode_selection, size_selection):
    mask =  (complete_df['date'].astype('datetime64').dt.date.between(start_date, end_date)) & (complete_df['year'] == year) & (complete_df['customer_PO'].isin(po_selection)) & (complete_df['name'].isin(customer_selection)) & (complete_df['opr_code'].isin(opr_selection)) & (complete_df['mastercode'].isin(mastercode_selection)) & (complete_df['size'].isin(size_selection))
    complete_df = complete_df[mask]
    
    complete_df = complete_df.dropna(subset = ['mastercode', 'size']) #adding mastercode == nan will increase the number of co
    complete_df["h_target"] = complete_df["h_target"].apply(lambda x : 50 if x == 0 else x) 
    #complete_df = complete_df[pd.notna(complete_df['mastercode'])]
    total_output = complete_df['qty'].sum()
    total_target = complete_df['target'].sum()
    total_co = complete_df['C/O'].sum()
    
    total_percent_co = (total_co/len(complete_df['C/O']))*100
    avg_efficiency = (complete_df["% Eff"].mean())*100
    avg_throughput = complete_df['Hourly Throughput'].mean()
    complete_df["% Eff"]  = (complete_df['% Eff'])*100

    sorted_months = complete_df.groupby(by='Month', as_index=False)['month_no'].first()
    
    co_by_month = complete_df.groupby(by='Month', as_index=False)['C/O'].sum()
    executions_by_month = complete_df.groupby(by='Month', as_index=False)['C/O'].count().rename(columns={'C/O':'count_co'})
    co_exe_by_month = pd.merge(left=co_by_month, right=executions_by_month, on='Month', how='left')
    co_exe_by_month['percent_co'] = (co_exe_by_month['C/O']/co_exe_by_month['count_co'])*100
    co_exe_by_month = co_exe_by_month.drop(columns=['C/O', 'count_co'])
    co_exe_by_month = pd.merge(left=co_exe_by_month, right=sorted_months, how='left').sort_values(by='month_no', ascending= True).drop(columns=['month_no'])
    eff_by_month = complete_df.groupby(by='Month', as_index=False)['% Eff'].mean()
    eff_by_month = pd.merge(left=eff_by_month, right=sorted_months, how='left').sort_values(by='month_no', ascending=True).drop(columns=['month_no'])
    eff_by_month['% Eff'] = eff_by_month['% Eff']
    throughput_by_month = complete_df.groupby(by='Month', as_index=False)['Hourly Throughput'].mean()
    throughput_by_month = pd.merge(left=throughput_by_month, right=sorted_months, how='left').sort_values(by='month_no', ascending=True).drop(columns=['month_no'])
    
    customer_wise_throughput = complete_df.groupby('SubCategory', as_index=False)['Hourly Throughput'].mean()
    customer_wise_eff = complete_df.groupby('SubCategory', as_index=False)['% Eff'].mean()
    customer_wise_eff_thr = pd.merge(left=customer_wise_throughput, right=customer_wise_eff, how='left').sort_values(by='% Eff', ascending = False)
    line_wise_throughput = complete_df.groupby('opr_code', as_index=False)['Hourly Throughput'].mean()
    line_wise_eff = complete_df.groupby('opr_code', as_index=False)['% Eff'].mean()
    line_wise_eff_thr = pd.merge(left=line_wise_throughput, right=line_wise_eff, how='left').sort_values(by='% Eff', ascending = False)
    
    customer_qty = complete_df.groupby(by='SubCategory', as_index=False)['qty'].sum().rename(columns={'SubCategory':'Customer Name', 'qty': 'Quantity'})
    
    co_by_brand = complete_df.groupby(by='SubCategory', as_index=False)['C/O'].sum()
    co_by_line = complete_df.groupby(by='opr_code', as_index=False)['C/O'].sum()
    return complete_df, total_output, total_target, total_co, total_percent_co, avg_efficiency, avg_throughput , sorted_months, co_exe_by_month,eff_by_month, throughput_by_month, customer_wise_eff_thr, line_wise_eff_thr, customer_qty, co_by_brand, co_by_line

@st.cache(suppress_st_warning=True, allow_output_mutation=True, ttl = 150)
def preprocess_auto_lastworking(complete_df):
    total_output = complete_df['qty'].sum()
    total_target = complete_df['target'].sum()
    total_co = complete_df['C/O'].sum()
    
    total_percent_co = (total_co/len(complete_df['C/O']))*100
    avg_efficiency = (complete_df["% Eff"].mean())*100
    avg_throughput = complete_df['Hourly Throughput'].mean()
    complete_df["% Eff"]  = (complete_df['% Eff'])*100

    sorted_months = complete_df.groupby(by='Month', as_index=False)['month_no'].first()
    
    co_by_month = complete_df.groupby(by='Month', as_index=False)['C/O'].sum()
    executions_by_month = complete_df.groupby(by='Month', as_index=False)['C/O'].count().rename(columns={'C/O':'count_co'})
    co_exe_by_month = pd.merge(left=co_by_month, right=executions_by_month, on='Month', how='left')
    co_exe_by_month['percent_co'] = (co_exe_by_month['C/O']/co_exe_by_month['count_co'])*100
    co_exe_by_month = co_exe_by_month.drop(columns=['C/O', 'count_co'])
    co_exe_by_month = pd.merge(left=co_exe_by_month, right=sorted_months, how='left').sort_values(by='month_no', ascending= True).drop(columns=['month_no'])
    eff_by_month = complete_df.groupby(by='Month', as_index=False)['% Eff'].mean()
    eff_by_month = pd.merge(left=eff_by_month, right=sorted_months, how='left').sort_values(by='month_no', ascending=True).drop(columns=['month_no'])
    eff_by_month['% Eff'] = eff_by_month['% Eff'] *100
    throughput_by_month = complete_df.groupby(by='Month', as_index=False)['Hourly Throughput'].mean()
    throughput_by_month = pd.merge(left=throughput_by_month, right=sorted_months, how='left').sort_values(by='month_no', ascending=True).drop(columns=['month_no'])
    
    customer_wise_throughput = complete_df.groupby('SubCategory', as_index=False)['Hourly Throughput'].mean()
    customer_wise_eff = complete_df.groupby('SubCategory', as_index=False)['% Eff'].mean()
    customer_wise_eff_thr = pd.merge(left=customer_wise_throughput, right=customer_wise_eff, how='left').sort_values(by='% Eff', ascending = False)
    line_wise_throughput = complete_df.groupby('opr_code', as_index=False)['Hourly Throughput'].mean()
    line_wise_eff = complete_df.groupby('opr_code', as_index=False)['% Eff'].mean()
    line_wise_eff_thr = pd.merge(left=line_wise_throughput, right=line_wise_eff, how='left').sort_values(by='% Eff', ascending = False)
    
    customer_qty = complete_df.groupby(by='SubCategory', as_index=False)['qty'].sum().rename(columns={'SubCategory':'Customer Name', 'qty': 'Quantity'})
    
    co_by_brand = complete_df.groupby(by='SubCategory', as_index=False)['C/O'].sum()
    co_by_line = complete_df.groupby(by='opr_code', as_index=False)['C/O'].sum()
    co_by_line = co_by_line[co_by_line['C/O'] != 0]

    planned_vs_target = complete_df.groupby('opr_code', as_index=False)[['qty','target']].sum().rename(columns={'qty':'Output', 'target':'Target'}).astype({'Output':int, 'Target': int})
    
    return complete_df, total_output, total_target, total_co, total_percent_co, avg_efficiency, avg_throughput , sorted_months, executions_by_month ,eff_by_month, throughput_by_month, customer_wise_eff_thr, line_wise_eff_thr, customer_qty, co_by_brand, co_by_line, planned_vs_target

def get_pro_lab_cost():
    cursor_sql_wh , conn_sql_wh = connect_sql_olap()
    pro_lab_cost = pd.read_sql_query("SELECT * FROM pro_lab_cost", conn_sql_wh)
    #pro_lab_cost = pd.DataFrame(pro_lab_cost, columns=["line_number", "Labor Cost", "month_year"])
    return pro_lab_cost
def get_foh_data():
    cursor_sql_wh , conn_sql_wh = connect_sql_olap()
    foh_df = pd.read_sql_query("SELECT * FROM monthly_foh", conn_sql_wh)
    foh_df.rename(columns={"FOH_VALUE": "FOH ($)", "TARGET_FOH": "Target FOH (%)"}, inplace = True)
    #foh_df = pd.DataFrame(foh_df, columns=["month_year", "FOH ($)", "Target FOH (%)"])
    return foh_df

@st.cache(suppress_st_warning=True, allow_output_mutation=True, ttl = 150)
def preprocess_costing(complete_df, start_date, end_date, year, po_selection, customer_selection, line_selection, mastercode_selection, size_selection, lwd=False):
    if lwd==False:
        mask =  (complete_df['date'].astype('datetime64').dt.date.between(start_date, end_date)) & (complete_df['year'] == year) & (complete_df['customer_PO'].isin(po_selection)) & (complete_df['name'].isin(customer_selection)) & (complete_df['line_number'].isin(line_selection)) & (complete_df['mastercode'].isin(mastercode_selection)) & (complete_df['size'].isin(size_selection))
        complete_df = complete_df[mask]
    complete_df['selling_price'] = complete_df['qty'].mul(complete_df['unitPrice'])
    customer_wise_throughput = complete_df.groupby('SubCategory', as_index=False)['Hourly Throughput'].mean()

    pro_lab_cost = get_pro_lab_cost()
    foh_df = get_foh_data()

    avg_throughput = complete_df['Hourly Throughput'].mean()
    complete_df['month_year'] = (complete_df['Month'])+(complete_df['year'].astype(str))
    sorted_months = complete_df.groupby(by='Month', as_index=False)['month_no'].first()
    linewise_monthly_sales_value = complete_df.groupby(['line_number', 'month_year'], as_index=False).sum()[['line_number', 'month_year', 'qty', 'selling_price']]
    linewise_monthly_sales_value['Month'] = linewise_monthly_sales_value['month_year'].apply(lambda x :x[0:3])
    pro_lab_cost['Labor Cost'] = pro_lab_cost['labor_cost'].astype(float)
    linewise_monthly_sales_value = linewise_monthly_sales_value.merge(pro_lab_cost, left_on=['line_number', 'month_year'], right_on=['line_number', 'month_year'], how='left')
    linewise_monthly_sales_value['per_pair_labor_cost'] = np.where(linewise_monthly_sales_value['Labor Cost'].astype(float)>0, linewise_monthly_sales_value['Labor Cost'].astype(float).div(linewise_monthly_sales_value['qty'].astype(float)),np.nan)
    ################################## Monthwise Analysis #####################################################################################
    throughput_by_month = complete_df.groupby(by='Month', as_index=False)['Hourly Throughput'].mean()
    throughput_by_month = pd.merge(left=throughput_by_month, right=sorted_months, how='left').sort_values(by='month_no', ascending=True).drop(columns=['month_no'])
    
    monthly_foh = complete_df.groupby('month_year').sum()['selling_price'].reset_index().merge(foh_df, how='left', on='month_year')
    monthly_foh['FOH (%)'] =  np.where(monthly_foh['FOH ($)'].astype(float)>0, monthly_foh['FOH ($)'].astype(float).div(monthly_foh['selling_price'].astype(float)),np.nan)
    monthly_foh['Month'] = monthly_foh['month_year'].apply(lambda x :x[0:3])
    monthly_foh['month_number'] = monthly_foh['Month'].apply(lambda x: list(calendar.month_abbr).index(x))
    monthly_foh = monthly_foh.drop(columns=['month_year']).sort_values(by='month_number', ascending= True)
    monthly_foh['FOH (%)'], monthly_foh['Target FOH (%)'] = monthly_foh['FOH (%)']*100 , monthly_foh['Target FOH (%)']*100
    customer_qty = complete_df.groupby(by='SubCategory', as_index=False)['qty'].sum().rename(columns={'SubCategory':'Customer Name', 'qty': 'Quantity'})
    customer_selling_price = complete_df.groupby(by='SubCategory', as_index=False)['selling_price'].sum().rename(columns={'SubCategory':'Customer Name', 'selling_price': 'Sales Value'})

    monthly_lab_cost = linewise_monthly_sales_value.groupby('Month').sum()[['qty', 'Labor Cost']].reset_index()
    monthly_lab_cost['per_pair_labor_cost'] = np.where(monthly_lab_cost['Labor Cost'].astype(float)>0, monthly_lab_cost['Labor Cost'].astype(float).div(monthly_lab_cost['qty'].astype(float)),np.nan)
    monthly_lab_cost['month_number'] = monthly_lab_cost['Month'].apply(lambda x: list(calendar.month_abbr).index(x))
    monthly_lab_cost.sort_values(by='month_number', ascending=True, inplace=True)
    monthly_lab_cost.drop(columns = ['month_number'], inplace=True)
    
    monthly_throughput_cost_foh = throughput_by_month.merge(monthly_lab_cost, how='left', on='Month').reset_index(drop=True)
    monthly_throughput_cost_foh = monthly_throughput_cost_foh.merge(monthly_foh, how='left', on='Month').reset_index(drop=True).drop(columns=['month_number'])
    #linewise_monthly_sales_value['month_number'] = linewise_monthly_sales_value['Month'].apply(lambda x: list(calendar.month_abbr).index(x))
    #linewise_monthly_sales_value = linewise_monthly_sales_value.drop(columns=['month_year']).sort_values(by='month_number', ascending= True)
#####################################################Linewise Analysis ###############################################################################
    line_wise_throughput = complete_df.groupby('line_number', as_index=False)['Hourly Throughput'].mean()
    linewise_lab_cost = linewise_monthly_sales_value.groupby('line_number', as_index=False).sum()[['line_number','qty', 'selling_price', 'Labor Cost']]
    linewise_lab_cost['per_pair_labor_cost'] = np.where(linewise_lab_cost['Labor Cost'].astype(float)>0, linewise_lab_cost['Labor Cost'].astype(float).div(linewise_lab_cost['qty'].astype(float)),np.nan)
    linewise_lab_cost = linewise_lab_cost.merge(line_wise_throughput, on='line_number', how='left')

    count_lines = complete_df.groupby('date')['line_number'].nunique().reset_index().rename(columns={'line_number':'line_count'})
    count_lines['date'] = count_lines['date'].astype('datetime64')
    complete_df = complete_df.merge(count_lines, how='left', on='date').merge(foh_df, how='left', on='month_year')
    complete_df['FOH($)'] = np.where(pd.notnull(complete_df['FOH ($)']), complete_df['FOH ($)'].astype(float).div(complete_df['line_count']),np.nan)
    complete_df = complete_df[['date', 'sale_order', 'customer_PO', 'production_order', 'line_number', 'description', 'qty', 'total_hours', 'Month', 'Hourly Throughput', 'selling_price', 'FOH($)', 'Target FOH (%)']]
    complete_df['FOH(%)'] = np.where(complete_df['FOH($)']>0, complete_df['FOH($)'].astype(float).div(complete_df['selling_price'].astype(float)),np.nan)
    
    #monthly_foh = complete_df.groupby('month_year').sum()['selling_price'].reset_index().merge(foh_df, how='left', on='month_year')
    #monthly_foh['FOH (%)'] =  np.where(monthly_foh['FOH ($)'].astype(float)>0, monthly_foh['FOH ($)'].astype(float).div(monthly_foh['selling_price'].astype(float)),np.nan)
    #linewise_monthly_sales_value['FOH(%)'] = np.where(linewise_monthly_sales_value['FOH ($)'].astype(float)>0, linewise_monthly_sales_value['selling_price'].astype(float).div(linewise_monthly_sales_value['FOH ($)'].astype(float)),np.nan)
    linewise_foh = complete_df.groupby('line_number', as_index=False).sum()[['line_number', 'FOH($)']]
    linewise_cost_foh = linewise_lab_cost.merge(linewise_foh, how="left", on="line_number")
    linewise_cost_foh['FOH (%)'] = np.where(linewise_cost_foh['FOH($)']>0, linewise_cost_foh['FOH($)'].astype(float).div(linewise_cost_foh['selling_price'].astype(float)),np.nan)
    linewise_cost_foh.sort_values(by='FOH (%)', ascending=False, inplace=True)
    del monthly_lab_cost, throughput_by_month, monthly_foh, sorted_months, customer_wise_throughput, line_wise_throughput, linewise_monthly_sales_value
    linewise_cost_foh = linewise_cost_foh.round(decimals = 2)
    return complete_df, avg_throughput ,monthly_throughput_cost_foh,  customer_qty ,customer_selling_price, linewise_cost_foh

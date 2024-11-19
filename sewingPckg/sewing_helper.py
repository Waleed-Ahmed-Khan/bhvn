import pandas as pd 
import streamlit as st
from common import helper ,sqlDBManagement
import appConfig as CONFIG


def preprocess_performance_form(df, month, year):
    sheets = ['LINE 1', 'LINE 2', 'LINE 3', 'LINE 4', 'LINE 5', 'LINE 6', 'LINE 7', 'LINE 9', 'LINE 10']

    performance = pd.concat([pd.read_excel(df, sheet_name=s, header=3, comment="#").assign(sheet_name=s) for s in sheets])
    performance = performance[(pd.notnull(performance['Card No']) & (pd.notnull(performance['Opeartion Code / \nSo Cong Doan']))) | pd.notnull(performance['Opeartion Code / \nSo Cong Doan'])]
    performance = performance[['Card No', 'Full Name', 'Designation', 'Joining Date', 'sheet_name', 'Opeartion Code / \nSo Cong Doan', 'Operation',
                            'Machine Type', 'Hourly Target ', 'Acutal Performance / Tong So Luong', 'Article', 'PB VND', 'Date', 'Pr/Hr', 
                            '% Efficiency ', 'Daily Target ','Time Loss (min)', 'Day']]
    performance = performance.rename({'Card No':'EmployeeCode', 'Full Name':'Name', 'Joining Date': 'JoiningDate','sheet_name':'Line', 'Opeartion Code / \nSo Cong Doan':'OperationCode',
                                    'Machine Type':'MachineType', 'Hourly Target ':'HourlyTarget', 'Acutal Performance / Tong So Luong':'Output', 'PB VND':'pbVND',
                                    'Pr/Hr':'Pr_per_HR','% Efficiency ':'Eff', 'Daily Target ':'DailyTarget','Time Loss (min)':'TimeLoss'}, axis = 1)
    cols = ['EmployeeCode', 'Name', 'Designation', 'JoiningDate', 'Line']
    performance.loc[:,cols] = performance.loc[:,cols].ffill()
    performance[['pbVND', 'TimeLoss']] = performance[['pbVND', 'TimeLoss']].fillna(0)
    performance['month_year'] = str(month)+str(year)
    return performance

@st.cache(suppress_st_warning=True, ttl = 160, show_spinner=False)
def get_performance_variables ():
    # if "bhvnMysql" not in st.session_state:
    #     st.session_state["bhvnMysql"] = helper.sqlDBManagement(host = helper.OLAP_HOST, username = helper.OLAP_USER_NAME,
    #                         password = helper.SQL_DWH_PASS, database = helper.OLAP_DB_NAME)
    if CONFIG.BHVN_CENT_DB_SESSION not in st.session_state:
        st.session_state[CONFIG.BHVN_CENT_DB_SESSION] = sqlDBManagement(host = helper.DB_CENT_HOST, username = helper.DB_CENT_USR,
                            password = helper.DB_CENT_PASS, database = helper.DB_CENT_NAME)

    db_engine = st.session_state[CONFIG.BHVN_CENT_DB_SESSION].engine
    performance = pd.read_sql("tblwrkperformance", db_engine)
    emp_code_list = performance['EmployeeCode'].unique().tolist()
    line_list = performance['Line'].unique().tolist()
    line_list.insert(0, 'All Lines')
    date = performance['Date'].unique().tolist()
    performance = performance.drop_duplicates(keep='first')
    return performance, emp_code_list, line_list, date

def preprocess_performance_data(performance,emp_code_selection, line_selection, start_date, end_date):
    mask = (performance['Date'].astype('datetime64').dt.date.between(start_date, end_date)) & (performance['EmployeeCode'] == emp_code_selection) & (performance['Line'].isin(line_selection)) 
    performance = performance.loc[mask].rename(columns={'eff':'Efficiency', 'Pr_per_Hr':'HourlyThroughput'})
    operation_wise = performance.groupby(by='Operation', as_index=False, dropna=True)[['Operation', 'Efficiency', 'HourlyThroughput', 'TimeLoss', 'pbVND']].mean()
    line_wise = performance.groupby(by='Line', as_index=False, dropna=True)[['Operation', 'Efficiency', 'HourlyThroughput', 'TimeLoss', 'pbVND']].mean()
    machine_wise = performance.groupby(by='MachineType', as_index=False, dropna=True)[['Operation', 'Efficiency', 'HourlyThroughput', 'TimeLoss', 'pbVND']].mean()
    operation_wise = operation_wise.sort_values(by='Efficiency', ascending=True)
    return performance, operation_wise, machine_wise, line_wise
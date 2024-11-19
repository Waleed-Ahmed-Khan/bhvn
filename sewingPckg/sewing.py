import pandas as pd 
import streamlit as st
from common import helper
import numpy as np
import plotly.graph_objects as go
import calendar
import static.formatHelper as fh
from datetime import datetime
from sewingPckg.sewing_main import render_sewing_operations, render_recent_working_day, render_sewing_form, render_performance_report
from streamlit_option_menu import option_menu
from st_aggrid import AgGrid

@st.cache(suppress_st_warning=True, allow_output_mutation=True, ttl=500, show_spinner=False)
def get_complete_sewing_data():
    query = '''
    SELECT p.date, p.orderno AS "sale_order", p.ponumber AS "customer_PO", 
    p.ProductionNo AS "production_order", p.section, sec.name as "opr_code", 
    p_det.itemid, p_det.partid, ItemsTable.description,
    working_hours, overtime_hours, tbl_itempart.description AS "Part", p_det.qty, repaired_qty, defect_id,  reject_qty
    FROM bhvnerp_bhv2019.tblproduction_detail p_det
    left join bhvnerp_bhv2019.tblproduction p on p_det.entryno = p.entryno
    left join tbl_section sec on p.section = sec.id
    left join tbl_itempart on p_det.partid = tbl_itempart.id
    left join tblitems on p_det.itemid = tblitems.itemid
    left join ItemsTable on p_det.itemid = ItemsTable.itemid
    where  (p_det.entryno like'%RFS%') and p.date >= '2022-01-01';
    '''
    sewing_transactions = helper.load_data(query)
    sewing_transactions = sewing_transactions.drop(['partid', 'section', 'Part', 'reject_qty', 'repaired_qty', 'defect_id'], axis=1)
    sewing_transactions= sewing_transactions.astype({'itemid':'int64'})

    sewing_transactions['total_hours'] = sewing_transactions['working_hours'] + sewing_transactions['overtime_hours']
    sewing_transactions = sewing_transactions[sewing_transactions['total_hours'] > 0] 
    sewing_transactions = sewing_transactions.rename(columns={'opr_code':'line_number'})
    sewing_transactions = sewing_transactions.drop_duplicates(keep="first")
    query = '''
    SELECT itemid,tblitems.mastercode, itemcode, description,size, tblitems.h_target, itemtype, cat.name AS Category,sub_cat.name AS SubCategory,inv.unitname,
    unitPrice, subcatid, categoryid, brandid, brand.name, tblitems.entrydate AS DateOfIntroduction
    FROM tblitems
    LEFT JOIN tblitemcategory AS cat ON tblitems.categoryid = cat.id
    LEFT JOIN pro_sub_cat AS sub_cat ON tblitems.subcatid = sub_cat.id
    LEFT JOIN tblinventoryunitname AS inv ON tblitems.masterpackingunitid = inv.id
    lEFT JOIN pro_item_brand as brand ON tblitems.brandid = brand.id
    ;
    '''
    # -- WHERE cat.name = "Finished Goods " #This is the last line from the above query
    tblitems = helper.load_data(query)
    tblitems = tblitems[tblitems.mastercode != '']
    tblitems = tblitems[['itemid', 'mastercode', 'itemcode', 'size', 'h_target',
            'SubCategory', 'unitPrice', 'name', 'DateOfIntroduction']]
    tblitems["h_target"] = tblitems["h_target"].apply(lambda x : 110 if x == 0 or pd.isnull(x) else x) 
    current_date = datetime.today().strftime('%Y-%m-%d')
    current_date = pd.to_datetime(current_date)
    tblitems['DateOfIntroduction'] = pd.to_datetime(tblitems['DateOfIntroduction'])
    product_age =  round(((current_date -  tblitems['DateOfIntroduction'])/pd.Timedelta(1,unit='d'))/30, 0)
    tblitems['product_age'] = product_age
    tblitems = tblitems.drop_duplicates(keep='first')
    complete_df = pd.merge(sewing_transactions, tblitems, how='left', on = 'itemid')
    complete_df = complete_df.drop_duplicates(keep='first')
    complete_df[['date1','line_number1', 'mastercode1']] = complete_df[['date','line_number', 'mastercode']].shift()
    is_co = []
    for index, row in complete_df.iterrows():
        if row['date'] == row ['date1'] and row['line_number'] == row ['line_number1'] and row['mastercode'] != row['mastercode1']:
            is_co.append('Yes')
        else:
            is_co.append('No')
    complete_df['is_co'] = is_co

    complete_df['C/O'] = [1 if i=='Yes' else 0 for i in is_co]
    complete_df = complete_df.drop(['date1','line_number1', 'mastercode1'], axis = 1)
    #st.dataframe(complete_df[['date','line_number', 'mastercode', 'date1','line_number1', 'mastercode1','is_co', 'C/O']])
    complete_df['target'] = complete_df['total_hours'] * complete_df['h_target']
    complete_df['DateOfIntroduction'] = [ pd.to_datetime(x).strftime("%Y-%m-%d") if pd.notna(x) else np.nan for x in complete_df['DateOfIntroduction']]
    complete_df['month_no'] = pd.to_datetime(complete_df['date']).dt.month
    complete_df['day_no'] = pd.to_datetime(complete_df['date']).dt.weekday 
    complete_df['year'] = pd.to_datetime(complete_df['date']).dt.year
    complete_df['Month'] = [calendar.month_name[i][0:3] for i in complete_df['month_no']]                             
    complete_df['Day'] = [calendar.day_name[i][0:3] for i in complete_df['day_no']]
    complete_df["% Eff"] = round((complete_df['qty']/ complete_df['target']), 2)
    complete_df['Hourly Throughput'] = round((complete_df['qty'] / complete_df['total_hours']), 0)
    complete_df['date'] = complete_df['date'].astype('datetime64')
    return complete_df


def render_sewing(username):
    st.write('<style>div.row-widget.stButton > div{flex-direction:row;} </style>', unsafe_allow_html=True)
    st.write('<style>div.st-bf{flex-direction:column;} div.st-ag{font-weight:bold;padding-left:2px;}</style>', unsafe_allow_html=True)
    st.write(fh.format_st_button(), unsafe_allow_html=True)

    selection = option_menu(

                menu_title = "Sewing Department",
                options = ['Sewing Operations', 'Last Working Day','Worker Performance', 'Sewing Forms' ],
                icons = ["mouse3-fill", "alarm-fill", "file-earmark-bar-graph-fill", "journal-text"],
                menu_icon = ["hospital-fill"],
                orientation = "horizontal"
    )

    try:
        if selection == "Sewing Operations":
            render_sewing_operations(username)
        elif selection == "Last Working Day":
            render_recent_working_day(username)
        elif selection == "Sewing Forms":
            render_sewing_form(username)
        elif selection == "Worker Performance":
            render_performance_report(username)
    except Exception as e:
        raise e
        #st.error(f"Dear {str.title(username)}, Something went wrong. Please contact admin in case the problem persists. We are sorry 😌")
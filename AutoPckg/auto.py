import pandas as pd 
import streamlit as st
from common import helper
import numpy as np
import calendar
import static.formatHelper as fh
from datetime import datetime
from AutoPckg.auto_main import render_auto_operations , render_recent_working_day
from streamlit_option_menu import option_menu
from st_aggrid import AgGrid

@st.cache(suppress_st_warning=True, allow_output_mutation=True, ttl=500, show_spinner=False)
def get_complete_auto_data():
    query = '''
    SELECT p.date, p.orderno AS sale_order, p.ponumber AS customer_PO, p.ProductionNo AS production_order,
    p.order_itemid,sec.name as opr_code,p_det.partid,tblitems.description, tbl_machines.machine,targets.fromdate,
    targets.todate, targets.target AS h_target, p_det.qty, defects.TotalPassedQty,working_hours,
    overtime_hours, p_det.ms_hours, tbl_itempart.description AS Part, defects.TotalDefectQty
    FROM bhvnerp_bhv2019.tblproduction_detail p_det
    LEFT JOIN bhvnerp_bhv2019.tblproduction p ON p_det.entryno = p.entryno
    LEFT JOIN tbl_section sec ON p.section = sec.id
    LEFT JOIN tbl_itempart ON p_det.partid = tbl_itempart.id
    LEFT JOIN tblitems ON p_det.itemid = tblitems.itemid
    LEFT JOIN autoTimeTargets targets ON p.order_itemid = targets.finish_itemid AND p_det.partid = targets.auto_itemid 
        AND p.date BETWEEN targets.fromdate AND targets.todate
    LEFT JOIN tblautomationdefects_quantity AS defects ON p.orderno = defects.orderno AND 
        p.ProductionNo = defects.ProductionNo AND p.ponumber = defects.ponumber AND p.deptid = defects.dept_id 
        AND p.section = defects.section_id AND p.order_itemid = defects.itemid AND p.date = defects.date
    LEFT JOIN tbl_machines ON p.machineid = tbl_machines.id AND p.deptid = tbl_machines.dept_id
    WHERE  (p_det.entryno LIKE'%AT%') AND p.date >= '2021-01-01' AND p.deptid = 37;
    '''
    auto_transactions = helper.load_data(query)
    auto_transactions = auto_transactions.drop_duplicates(keep='first')
    #auto_transactions = auto_transactions.drop(['Item', 'section',], axis=1 )
    #auto_transactions= auto_transactions.astype({'itemid':'int64'})
    
    auto_transactions['total_hours'] = auto_transactions['working_hours'] + auto_transactions['overtime_hours']
    auto_transactions = auto_transactions[auto_transactions['total_hours'] > 0] 
    auto_transactions['% DR'] = round((auto_transactions['TotalDefectQty'].div(auto_transactions['qty'].values, axis=0))*100, 2)

    query = '''

    SELECT itemid,mastercode, itemcode,size, itemtype, cat.name AS Category,sub_cat.name AS SubCategory,inv.unitname,
    unitPrice, brand.name, tblitems.entrydate AS DateOfIntroduction
    FROM tblitems
    LEFT JOIN tblitemcategory AS cat ON tblitems.categoryid = cat.id
    LEFT JOIN pro_sub_cat AS sub_cat ON tblitems.subcatid = sub_cat.id
    LEFT JOIN tblinventoryunitname AS inv ON tblitems.masterpackingunitid = inv.id
    lEFT JOIN pro_item_brand as brand ON tblitems.brandid = brand.id
    ;

    '''
    tblitems = helper.load_data(query)
    tblitems = tblitems[tblitems.mastercode != '']
    tblitems = tblitems[['itemid', 'mastercode', 'itemcode', 'size',
            'SubCategory', 'unitPrice', 'name', 'DateOfIntroduction']]
    auto_transactions["h_target"] = auto_transactions["h_target"].apply(lambda x : 30 if x == 0 or pd.isnull(x) else x) 
    current_date = datetime.today().strftime('%Y-%m-%d')
    current_date = pd.to_datetime(current_date)
    tblitems['DateOfIntroduction'] = pd.to_datetime(tblitems['DateOfIntroduction'])
    product_age =  round(((current_date -  tblitems['DateOfIntroduction'])/pd.Timedelta(1,unit='d'))/30, 0)
    tblitems['product_age'] = product_age
    tblitems = tblitems.drop_duplicates(keep='first')
    complete_df = pd.merge(auto_transactions, tblitems, left_on = "order_itemid", right_on="itemid", how = 'left')
    complete_df = complete_df.drop_duplicates(keep='first')
    #complete_df = complete_df.rename({'itemid_y':'itemid', 'name_y': 'name', 'mastercode_y':'mastercode'})
    complete_df[['date1','machine1', 'mastercode1']] = complete_df[['date','machine', 'mastercode']].shift()
    is_co = []
    for index, row in complete_df.iterrows():
        if pd.notna(row['mastercode']):
            if row['date'] == row ['date1'] and row['machine'] == row ['machine1'] and row['mastercode'] != row['mastercode1']:
                is_co.append('Yes')
            else:
                is_co.append('No')
        else:
            is_co.append('No')
    complete_df['is_co'] = is_co

    complete_df['C/O'] = [1 if i=='Yes' else 0 for i in is_co]
    complete_df = complete_df.drop(['date1','machine1', 'mastercode1'], axis = 1)
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


def render_auto(username):

    st.write('<style>div.row-widget.stButton > div{flex-direction:row;} </style>', unsafe_allow_html=True)
    st.write('<style>div.st-bf{flex-direction:column;} div.st-ag{font-weight:bold;padding-left:2px;}</style>', unsafe_allow_html=True)
    st.write(fh.format_st_button(), unsafe_allow_html=True)

    selection = option_menu(

                menu_title = "Automation Department",
                options = ['Automation Operations', 'Last Working Day'],
                icons = ["device-ssd-fill", "alarm-fill"],
                menu_icon = ["gear-wide-connected"],
                orientation = "horizontal"
    )

    try:
        if selection == 'Automation Operations':
            render_auto_operations(username)

        elif selection == 'Last Working Day':
            render_recent_working_day(username)
    except:
        st.error(f"Dear {str.title(username)}, Something went wrong. Please contact admin in case the problem persists. We are sorry 😌")
        

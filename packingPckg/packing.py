import pandas as pd 
import streamlit as st
from common import helper
import numpy as np
import plotly.graph_objects as go
import calendar
import static.formatHelper as fh
from datetime import datetime
from packingPckg.packing_main import render_packing_operations, render_recent_working_day
from streamlit_option_menu import option_menu

@st.cache(suppress_st_warning=True, allow_output_mutation=True, ttl=500, show_spinner=False)
def get_complete_packing_data():
    query = '''
    SELECT p.date, p.orderno AS "sale_order", p.ponumber AS "customer_PO", 
    p.ProductionNo AS "production_order",
    p_det.itemid, p_det.partid, ItemsTable.description,
    working_hours, overtime_hours, tbl_itempart.description AS "Part", p_det.qty, repaired_qty, defect_id,  reject_qty
    FROM bhvnerp_bhv2019.tblproduction_detail p_det
    left join bhvnerp_bhv2019.tblproduction p on p_det.entryno = p.entryno
    left join tbl_itempart on p_det.partid = tbl_itempart.id
    left join tblitems on p_det.itemid = tblitems.itemid
    left join ItemsTable on p_det.itemid = ItemsTable.itemid
    where  (p_det.entryno like'%RFP%') and p.date >= '2022-01-01' AND p.date < '2025-01-01';
    '''
    packing_transactions = helper.load_data(query)
    packing_transactions = packing_transactions.drop(['partid', 'Part', 'reject_qty', 'repaired_qty', 'defect_id'], axis=1)
    packing_transactions= packing_transactions.astype({'itemid':'int64'})
    packing_transactions['working_hours'] = packing_transactions['working_hours'].apply(lambda x : 8 if x == 0 or pd.isnull(x) else x)
    packing_transactions['overtime_hours'] = packing_transactions['overtime_hours'].apply(lambda x : 0 if x == 0 or pd.isnull(x) else x)
    # = packing_transactions['overtime_hours'].apply(lambda x : 0 if x == 0 or pd.isnull(x) else x)
    #packing_transactions['overtime_hours'] = np.where(packing_transactions['date']> pd.to_datetime("2022-05-01"), 1.5, 2)
    #packing_transactions['overtime_hours'] = [1.5 if x['C'] >  else x['overtime_hours']  for x in packing_transactions]
    packing_transactions['total_hours'] = packing_transactions['working_hours'] + packing_transactions['overtime_hours']
    packing_transactions = packing_transactions[packing_transactions['total_hours'] > 0] 
    packing_transactions = packing_transactions.rename(columns={'opr_code':'line_number'})
    packing_transactions = packing_transactions.drop_duplicates(keep="first")
    query = '''
    SELECT itemid,mastercode, itemcode, description,size, tblitems.h_target, itemtype, cat.name AS Category,sub_cat.name AS SubCategory,inv.unitname,
    unitPrice, subcatid, categoryid, brandid, brand.name, tblitems.entrydate AS DateOfIntroduction
    FROM tblitems
    LEFT JOIN tblitemcategory AS cat ON tblitems.categoryid = cat.id
    LEFT JOIN pro_sub_cat AS sub_cat ON tblitems.subcatid = sub_cat.id
    LEFT JOIN tblinventoryunitname AS inv ON tblitems.masterpackingunitid = inv.id
    lEFT JOIN pro_item_brand as brand ON tblitems.brandid = brand.id
    WHERE cat.name = "Finished Goods "
    ;
    '''
    tblitems = helper.load_data(query)
    tblitems = tblitems[tblitems.mastercode != '']
    tblitems = tblitems[['itemid', 'mastercode', 'itemcode', 'size', 'h_target',
            'SubCategory', 'unitPrice', 'name', 'DateOfIntroduction']]
    tblitems["h_target"] = tblitems["h_target"].apply(lambda x : 60 if x == 0 or pd.isnull(x) else x) 
    current_date = datetime.today().strftime('%Y-%m-%d')
    current_date = pd.to_datetime(current_date)
    tblitems['DateOfIntroduction'] = pd.to_datetime(tblitems['DateOfIntroduction'])
    product_age =  round(((current_date -  tblitems['DateOfIntroduction'])/pd.Timedelta(1,unit='d'))/30, 0)
    tblitems['product_age'] = product_age
    tblitems = tblitems.drop_duplicates(keep='first')
    complete_df = pd.merge(packing_transactions, tblitems, how='left', on = 'itemid')
    complete_df = complete_df.drop_duplicates(keep='first')
    complete_df[['date1', 'mastercode1']] = complete_df[['date', 'mastercode']].shift()
    is_co = []
    for index, row in complete_df.iterrows():
        if row['date'] == row ['date1'] and row['mastercode'] != row['mastercode1']:
            is_co.append('Yes')
        else:
            is_co.append('No')
    complete_df['is_co'] = is_co

    complete_df['C/O'] = [1 if i=='Yes' else 0 for i in is_co]
    complete_df = complete_df.drop(['date1', 'mastercode1'], axis = 1)
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


def render_packing(username):
    st.write('<style>div.row-widget.stButton > div{flex-direction:row;} </style>', unsafe_allow_html=True)
    st.write('<style>div.st-bf{flex-direction:column;} div.st-ag{font-weight:bold;padding-left:2px;}</style>', unsafe_allow_html=True)
    st.write(fh.format_st_button(), unsafe_allow_html=True)

    selection = option_menu(

                menu_title = "Packing Department",
                options = ['Packing Operations', 'Last Working Day'],
                icons = ["boxes", "alarm-fill"],
                menu_icon = ["box-seam"],
                orientation = "horizontal"
    )

    try:
        if selection == "Packing Operations":
            render_packing_operations(username)
        elif selection == "Last Working Day":
            render_recent_working_day(username)
    except Exception as e:
        raise e
        #st.error(f"Dear {str.title(username)}, Something went wrong. Please contact admin in case the problem persists. We are sorry 😌")
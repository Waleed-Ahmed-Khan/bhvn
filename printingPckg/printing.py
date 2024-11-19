import calendar
from datetime import datetime

import numpy as np
import pandas as pd
import static.formatHelper as fh
import streamlit as st
from common import helper
from streamlit_option_menu import option_menu
import random 

from printingPckg.printing_main import (render_printing_operations,
                                        render_recent_working_day)


@st.cache(suppress_st_warning=True, ttl=60, show_spinner=False)
def get_complete_printing_data():
    query = '''
    SELECT p.date, p.orderno AS sale_order, p.ponumber AS customer_PO, p.ProductionNo AS production_order,sec.name as station,
    p.order_itemid AS itemid,p_det.partid, tblitems.description,targets.fromdate,
    targets.todate, targets.target AS h_target, p_det.qty, p_det.defect_qty, rejection.name AS defect_type,working_hours,
    overtime_hours, tblprinting_items.description AS Part
    FROM bhvnerp_bhv2019.tblproduction_detail p_det
    LEFT JOIN bhvnerp_bhv2019.tblproduction p ON p_det.entryno = p.entryno
    left join tbl_section sec on p.section = sec.id
    LEFT JOIN tblprinting_items ON p_det.partid = tblprinting_items.printing_itemid
    LEFT JOIN tblitems ON tblprinting_items.finish_itemid= tblitems.itemid
    LEFT JOIN tblrejectiontypes rejection ON p_det.defect_id = rejection.id
    LEFT JOIN tblprinting_items_target targets ON tblprinting_items.finish_itemid = targets.finish_itemid AND  p_det.partid = targets.printing_itemid 
        AND p.date BETWEEN targets.fromdate AND targets.todate
    WHERE  (p_det.entryno LIKE'%PT%') AND p.date >= '2022-01-01';
    '''
    if "part_wise" not in st.session_state:
        part_wise = helper.load_data(query)
        #part_wise = part_wise.drop(['partid', 'section', 'Part', 'reject_qty', 'repaired_qty', 'defect_id'], axis=1)
        part_wise= part_wise.astype({'itemid':'int64'})

        part_wise['total_hours'] = part_wise['working_hours'] + part_wise['overtime_hours']
        part_wise = part_wise[part_wise['total_hours'] > 0] 
        part_wise = part_wise.drop_duplicates(keep="first")
        
        tbl_list = ['T1', 'T2', 'T3', 'T4', 'T5', 'HT1', 'E1', 'E2', 'E3', 'E4', 'E5', 'E6', 'HT2'] 
        part_wise['station'] = [random.choice(tbl_list) if pd.isnull(i) else i for i in part_wise['station']]
        st.session_state["part_wise"] = part_wise
    else:
        part_wise = st.session_state['part_wise']
        
    item_wise = part_wise.groupby(['date', 'sale_order', 'customer_PO', 'production_order','itemid', 'description', 'station'], as_index=False).agg(
        h_target = pd.NamedAgg('h_target', aggfunc='mean'),
        qty = pd.NamedAgg('qty', aggfunc='sum'),
        working_hours = pd.NamedAgg('working_hours', aggfunc='mean'),
        overtime_hours = pd.NamedAgg('overtime_hours', aggfunc='mean'),
        defect_qty = pd.NamedAgg('defect_qty', aggfunc='mean'),
        defect_type = pd.NamedAgg('defect_type', aggfunc='max')
    )


    query = '''
    SELECT itemid,mastercode, itemcode, description,size, itemtype, cat.name AS Category,sub_cat.name AS SubCategory,inv.unitname,
    unitPrice, subcatid, categoryid, brandid, brand.name, tblitems.entrydate AS DateOfIntroduction
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
    current_date = datetime.today().strftime('%Y-%m-%d')
    current_date = pd.to_datetime(current_date)
    tblitems['DateOfIntroduction'] = pd.to_datetime(tblitems['DateOfIntroduction'])
    product_age =  round(((current_date -  tblitems['DateOfIntroduction'])/pd.Timedelta(1,unit='d'))/30, 0)
    tblitems['product_age'] = product_age
    tblitems = tblitems.drop_duplicates(keep='first')
    complete_df = pd.merge(item_wise, tblitems, how='left', on = 'itemid')
    complete_df = complete_df.drop_duplicates(keep='first')
    complete_df[['date1','station1', 'mastercode1']] = complete_df[['date','station', 'mastercode']].shift()
    is_co = []
    for index, row in complete_df.iterrows():
        if row['date'] == row ['date1'] and row['station'] == row ['station1'] and row['mastercode'] != row['mastercode1']:
            is_co.append('Yes')
        else:
            is_co.append('No')
    complete_df['is_co'] = is_co

    complete_df['C/O'] = [1 if i=='Yes' else 0 for i in is_co]
    complete_df = complete_df.drop(['date1','station1', 'mastercode1'], axis = 1)
    #st.dataframe(complete_df[['date','line_number', 'mastercode', 'date1','line_number1', 'mastercode1','is_co', 'C/O']])
    complete_df["h_target"] = complete_df["h_target"].apply(lambda x : 50 if (x == 0 or pd.isnull(x)) else x) 
    complete_df['total_hours'] = complete_df['working_hours'] + complete_df['overtime_hours']
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


def render_printing(username):
    st.write('<style>div.row-widget.stButton > div{flex-direction:row;} </style>', unsafe_allow_html=True)
    st.write('<style>div.st-bf{flex-direction:column;} div.st-ag{font-weight:bold;padding-left:2px;}</style>', unsafe_allow_html=True)
    st.write(fh.format_st_button(), unsafe_allow_html=True)

    selection = option_menu(

                menu_title = "Printing Department",
                options = ['Printing Operations', 'Last Working Day'],
                icons = ["paint-bucket", "alarm-fill"],
                menu_icon = ["palette"],
                orientation = "horizontal"
    )

    try:
        if selection == "Printing Operations":
            render_printing_operations(username)
        elif selection == "Last Working Day":
            render_recent_working_day(username)
    except Exception as e:
        raise e
        st.error(f"Dear {str.title(username)}, Something went wrong. Please contact admin in case the problem persists. We are sorry 😌")

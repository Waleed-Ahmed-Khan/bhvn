import pandas as pd 
import streamlit as st
from common import helper
import numpy as np
import calendar
import static.formatHelper as fh
from datetime import datetime
from accountsPckg.costing.costing_main import render_costing_operations, render_recent_working_day, render_costing_form, render_salary_form
from streamlit_option_menu import option_menu
from accountsPckg.cm_dcl.cm_main import render_cm_dcl

@st.cache(suppress_st_warning=True)
def get_complete_costing_data():
    query = '''
    SELECT p.date, p.orderno AS "sale_order", p.ponumber AS "customer_PO", 
    p.ProductionNo AS "production_order", p.section, sec.name as "opr_code", 
    p_det.itemid, p_det.partid,tblitems.description AS "Item", ItemsTable.description,
    working_hours, overtime_hours, tbl_itempart.description AS "Part", p_det.qty, repaired_qty, defect_id,  reject_qty
    FROM bhvnerp_bhv2019.tblproduction_detail p_det
    left join bhvnerp_bhv2019.tblproduction p on p_det.entryno = p.entryno
    left join tbl_section sec on p.section = sec.id
    left join tbl_itempart on p_det.partid = tbl_itempart.id
    left join tblitems on p_det.itemid = tblitems.itemid
    left join ItemsTable on p_det.itemid = ItemsTable.itemid
    where  (p_det.entryno like'%RFS%') and p.date >= '2021-01-01';
    '''
    costing_transactions = helper.load_data(query)
    costing_transactions = costing_transactions.drop(['partid', 'Item', 'section', 'Part', 'reject_qty', 'repaired_qty', 'defect_id'], axis=1)
    costing_transactions= costing_transactions.astype({'itemid':'int64'})

    costing_transactions['total_hours'] = costing_transactions['working_hours'] + costing_transactions['overtime_hours']
    costing_transactions = costing_transactions[costing_transactions['total_hours'] > 0] 
    costing_transactions = costing_transactions.rename(columns={'opr_code':'line_number'})
    costing_transactions = costing_transactions.drop_duplicates(keep="first")
    query = '''
    SELECT itemid,mastercode, itemcode, description,size, h_target, itemtype, cat.name AS Category,sub_cat.name AS SubCategory,inv.unitname,
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
    tblitems = tblitems[['itemid', 'mastercode', 'itemcode', 'size', 'SubCategory', 'unitPrice', 'name', 'DateOfIntroduction']]
    current_date = datetime.today().strftime('%Y-%m-%d')
    current_date = pd.to_datetime(current_date)
    tblitems['DateOfIntroduction'] = pd.to_datetime(tblitems['DateOfIntroduction'])
    product_age =  round(((current_date -  tblitems['DateOfIntroduction'])/pd.Timedelta(1,unit='d'))/30, 0)
    tblitems['product_age'] = product_age
    tblitems = tblitems.drop_duplicates(keep='first')
    complete_df = pd.merge(costing_transactions, tblitems, how='left', on = 'itemid')
    complete_df = complete_df.drop_duplicates(keep='first')

    complete_df['DateOfIntroduction'] = [ pd.to_datetime(x).strftime("%Y-%m-%d") if pd.notna(x) else np.nan for x in complete_df['DateOfIntroduction']]
    complete_df['month_no'] = pd.to_datetime(complete_df['date']).dt.month
    complete_df['day_no'] = pd.to_datetime(complete_df['date']).dt.weekday 
    complete_df['year'] = pd.to_datetime(complete_df['date']).dt.year
    complete_df['Month'] = [calendar.month_name[i][0:3] for i in complete_df['month_no']]                             
    complete_df['Day'] = [calendar.day_name[i][0:3] for i in complete_df['day_no']]
    complete_df['Hourly Throughput'] = round((complete_df['qty'] / complete_df['total_hours']), 0)
    complete_df['date'] = complete_df['date'].astype('datetime64')
    return complete_df

def render_finance(username):
    st.write('<style>div.row-widget.stButton > div{flex-direction:row;} </style>', unsafe_allow_html=True)
    st.write('<style>div.st-bf{flex-direction:column;} div.st-ag{font-weight:bold;padding-left:2px;}</style>', unsafe_allow_html=True)
    st.write(fh.format_st_button(), unsafe_allow_html=True)
    '''
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        costing_dashboard =st.button("📈Costing Dashboard")
        if costing_dashboard:
            st.session_state['costing_dashboard'] = True
            st.session_state['last_working_day'] = False
            st.session_state['costing_form'] = False
    with col2:
        last_working_day = st.button("🧭Last Working Day")
        if last_working_day: 
            st.session_state['costing_dashboard'] = False
            st.session_state['last_working_day'] = True
            st.session_state['costing_form'] = False
    with col3:
        costing_form = st.button("📑Costing Form")
        if costing_form:
            st.session_state['costing_dashboard'] = False
            st.session_state['last_working_day'] = False
            st.session_state['costing_form'] = True
    with col4:
        st.write('')
    with col5:
        st.write('')
    '''
    selection = option_menu(

                menu_title = "Accounts & Finance",
                options = ['Cost Analysis','Costing Operations', 'Last Working Day', 'Costing Forms', 'Salary Form'],
                icons = ["bar-chart-steps", "wallet-fill", "alarm-fill", "journal-text", "card-checklist"],
                menu_icon = ["cash-coin"],
                orientation = "horizontal"
    )

    try:
        if selection == "Cost Analysis":
            render_cm_dcl()
        if selection == 'Costing Operations':
            render_costing_operations(username)

        elif selection == 'Last Working Day':
            render_recent_working_day(username)

        elif selection == 'Costing Forms':
            render_costing_form(username)
        elif selection == 'Salary Form':
            render_salary_form(username)
    except Exception as e:
        raise e
        #st.error(f"Dear {str.title(username)}, Something went wrong. Please contact admin in case the problem persists. We are sorry 😌")
        
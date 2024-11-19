from re import A
import pandas as pd
from common.sqlDBOperations import sqlDBManagement
from dotenv import load_dotenv
import os
import mysql.connector as sql
from datetime import datetime
from common import helper
from st_aggrid import AgGrid
import streamlit as st
import plotly.express as px
from static.formatHelper import hover_size
import plotly.graph_objects as go 
import appConfig as CONFIG

def render_cm_dcl():
    st.markdown(hover_size(), unsafe_allow_html=True)
    # bhvnMysql = sqlDBManagement(host = helper.OLAP_HOST, username = helper.OLAP_USER_NAME,
    #                         password = helper.SQL_DWH_PASS, database = helper.OLAP_DB_NAME)

    if CONFIG.BHVN_CENT_DB_SESSION not in st.session_state:
        st.session_state[CONFIG.BHVN_CENT_DB_SESSION] = sqlDBManagement(host = helper.DB_CENT_HOST, username = helper.DB_CENT_USR,
                            password = helper.DB_CENT_PASS, database = helper.DB_CENT_NAME)
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
    where  (p_det.entryno like'%RFS%') and p.date >= '2021-01-01';
    '''
    sewing_transactions = helper.load_data(query)
    sewing_transactions = sewing_transactions.drop(['partid', 'section', 'Part', 'reject_qty', 'repaired_qty', 'defect_id'], axis=1)
    sewing_transactions= sewing_transactions.astype({'itemid':'int64'})

    sewing_transactions['total_hours'] = sewing_transactions['working_hours'] + sewing_transactions['overtime_hours']
    sewing_transactions = sewing_transactions[sewing_transactions['total_hours'] > 0] 
    sewing_transactions = sewing_transactions.rename(columns={'opr_code':'line_number'})
    sewing_transactions = sewing_transactions.drop_duplicates(keep="first")

    query = '''
    SELECT itemid,mastercode, itemcode, description,size, tblitems.h_target, itemtype, cat.name AS Category,sub_cat.name AS SubCategory,inv.unitname,
    unitPrice, subcatid, categoryid, brandid, brand.name, tblitems.entrydate AS DateOfIntroduction
    FROM tblitems
    LEFT JOIN tblitemcategory AS cat ON tblitems.categoryid = cat.id
    LEFT JOIN pro_sub_cat AS sub_cat ON tblitems.subcatid = sub_cat.id
    LEFT JOIN tblinventoryunitname AS inv ON tblitems.masterpackingunitid = inv.id
    lEFT JOIN pro_item_brand as brand ON tblitems.brandid = brand.id
    WHERE cat.name = "Finished Goods " AND mastercode LIKE'%DCL%'
    ;
    '''
    # ("DCL-304140", "DCL-304140-G", "DCL-105335", "DCL-123676", "DCL-326446R", "DCL-326446G", "DCL-305595", "DCL-326444", "DCL-326444R", "DCL-326444G")
    tblitems = helper.load_data(query)
    tblitems = tblitems[tblitems.mastercode != '']
    tblitems = tblitems[['itemid', 'mastercode', 'itemcode', 'size', 'h_target',
            'SubCategory', 'unitPrice', 'name', 'DateOfIntroduction']]
    #tblitems["h_target"] = tblitems["h_target"].apply(lambda x : 60 if x == 0 or pd.isnull(x) else x) 
    current_date = datetime.today().strftime('%Y-%m-%d')
    current_date = pd.to_datetime(current_date)
    tblitems['DateOfIntroduction'] = pd.to_datetime(tblitems['DateOfIntroduction'])
    product_age =  round(((current_date -  tblitems['DateOfIntroduction'])/pd.Timedelta(1,unit='d'))/30, 0)
    tblitems['product_age'] = product_age
    tblitems = tblitems.drop_duplicates(keep='first')
    complete_df = pd.merge(sewing_transactions, tblitems, how='left', on = 'itemid')
    complete_df = complete_df.drop_duplicates(keep='first')
    complete_df['month'] = pd.to_datetime(complete_df['date']).dt.month_name().str.slice(stop=3)
    complete_df['year'] = pd.to_datetime(complete_df['date']).dt.year
    dcl_mastercodes = complete_df[pd.notnull(complete_df['mastercode'])]
    dcl_mastercodes = dcl_mastercodes.groupby(['year','mastercode'], as_index=False).agg(
        h_target = pd.NamedAgg('h_target', aggfunc='mean'),
        qty = pd.NamedAgg('qty', aggfunc='sum'),
        working_hours = pd.NamedAgg('total_hours', aggfunc='sum'),
        unit_price = pd.NamedAgg('unitPrice', aggfunc='mean'),
        product_age = pd.NamedAgg('product_age', aggfunc='mean'),
        date = pd.NamedAgg('date', aggfunc='min')
    )

    cm_dcl = st.session_state[CONFIG.BHVN_CENT_DB_SESSION].getDataFramebyQuery(query = "SELECT * FROM cm_dcl")
    cm_dcl['year'] = cm_dcl['year'].astype(int)
    dcl_mastercodes = pd.merge(cm_dcl, dcl_mastercodes, how='left', left_on=['year','mastercode'], right_on=['year', 'mastercode'])

    dcl_mastercodes['total_target'] = dcl_mastercodes['h_target'] * dcl_mastercodes['working_hours']
    dcl_mastercodes['Hourly Throughput'] = dcl_mastercodes['qty'] / dcl_mastercodes['working_hours']
    #dcl_mastercodes['standard_hours'] = dcl_mastercodes['qty'] / dcl_mastercodes['h_target']
    dcl_mastercodes['eff'] = (dcl_mastercodes['qty']/dcl_mastercodes['total_target']) * 100
    dcl_mastercodes['cost_of_mfg_actual'] = dcl_mastercodes['qty'] * dcl_mastercodes['price']
    dcl_mastercodes['cost_of_mfg_target'] = (dcl_mastercodes['eff']/100) * dcl_mastercodes['cost_of_mfg_actual']
    dcl_mastercodes['cost_variance'] = dcl_mastercodes['cost_of_mfg_actual'] - dcl_mastercodes['cost_of_mfg_target']
    cost_main = dcl_mastercodes[['date', 'mastercode',  'cost_of_mfg_target', 'cost_of_mfg_actual' ]].set_index('date').round(2)
    total_output = int(dcl_mastercodes['qty'].sum())
    total_target  = int(dcl_mastercodes['total_target'].sum())
    cost_of_mfg_actual = round(dcl_mastercodes['cost_of_mfg_actual'].sum(), 2)
    cost_of_mfg_target = round(dcl_mastercodes['cost_of_mfg_target'].sum(), 2)
    cost_variance = cost_of_mfg_actual - cost_of_mfg_target
    avg_hourly_target = int(dcl_mastercodes['h_target'].mean())
    avg_hourly_throughput =  int(dcl_mastercodes['Hourly Throughput'].mean())
    avg_eff = round(dcl_mastercodes['eff'].mean())

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<h4 style = 'text-align: center; color: red;'>Total Output Quantity</h3>", unsafe_allow_html= True)
        st.markdown(f"<h3 style = 'text-align: center; color: blue;'>{total_output} pairs</h1>", unsafe_allow_html= True)
    with col2:
        st.markdown(f"<h4 style = 'text-align: center; color: red;'>Total Target Quantity</h3>", unsafe_allow_html= True)
        st.markdown(f"<h3 style = 'text-align: center; color: blue;'>{total_target} pairs</h1>", unsafe_allow_html= True)
    with col3:
        st.markdown(f"<h4 style = 'text-align: center; color: red;'>Quantity Variance</h3>", unsafe_allow_html= True)
        st.markdown(f"<h3 style = 'text-align: center; color: blue;'>{total_output - total_target} pairs</h1>", unsafe_allow_html= True)
    col1, col2, col3 =  st.columns(3)
    with col1:
            st.markdown(f"<h4 style = 'text-align: center; color: red;'>Actual Cost of Manufacturing</h3>", unsafe_allow_html= True)
            st.markdown(f"<h3 style = 'text-align: center; color: blue;'>$ {cost_of_mfg_actual}</h1>", unsafe_allow_html= True)
    with col2:
        st.markdown(f"<h4 style = 'text-align: center; color: red;'>Target Cost of Manufacturing</h3>", unsafe_allow_html= True)
        st.markdown(f"<h3 style = 'text-align: center; color: blue;'>$ {cost_of_mfg_target}</h1>", unsafe_allow_html= True)
    with col3:
        st.markdown(f"<h4 style = 'text-align: center; color: red;'>Cost Variance</h3>", unsafe_allow_html= True)
        st.markdown(f"<h3 style = 'text-align: center; color: blue;'>$ {round(cost_variance, 2)}</h1>", unsafe_allow_html= True)
    col1, col2, col3 =  st.columns(3)
    with col1:
            st.markdown(f"<h4 style = 'text-align: center; color: red;'>Avg Hourly Throughput</h3>", unsafe_allow_html= True)
            st.markdown(f"<h3 style = 'text-align: center; color: blue;'>{avg_hourly_throughput} pairs</h1>", unsafe_allow_html= True)
    with col2:
        st.markdown(f"<h4 style = 'text-align: center; color: red;'>Avg Hourly Target</h3>", unsafe_allow_html= True)
        st.markdown(f"<h3 style = 'text-align: center; color: blue;'>{avg_hourly_target} pairs</h1>", unsafe_allow_html= True)
    with col3:
        st.markdown(f"<h4 style = 'text-align: center; color: red;'>Avg Efficiency</h3>", unsafe_allow_html= True)
        st.markdown(f"<h3 style = 'text-align: center; color: blue;'>{avg_eff} %</h1>", unsafe_allow_html= True)
    fig = px.area(cost_main, facet_col="mastercode", facet_col_wrap=4, width = 1300,height=600, title = 'Cost of Mfg($) Comparison')
    st.plotly_chart(fig)

    cost_variance = dcl_mastercodes[['date', 'mastercode',"cost_variance" ]].set_index('date').round(2)
    fig = px.area(cost_variance, facet_col="mastercode", facet_col_wrap=4, width = 1300,height=600, title = 'Cost Variance($)')
    st.plotly_chart(fig)

    cost_analysis_grouped = dcl_mastercodes.groupby(['mastercode'], as_index= False).agg(
                              cost_of_mfg_target = pd.NamedAgg('cost_of_mfg_target', aggfunc='sum'),
                              cost_of_mfg_actual = pd.NamedAgg('cost_of_mfg_actual', aggfunc='sum'),
                              cost_variance = pd.NamedAgg('cost_variance', aggfunc='sum')
    ).round(2)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Target Cost ($)", x=cost_analysis_grouped['mastercode'], y=cost_analysis_grouped['cost_of_mfg_target']))
    fig.add_trace(go.Bar(name="Actual Cost ($)", x=cost_analysis_grouped['mastercode'], y=cost_analysis_grouped['cost_of_mfg_target']))
    fig.add_trace(go.Bar(name="Cost Variance ($)", x=cost_analysis_grouped['mastercode'], y=cost_analysis_grouped['cost_variance']))
    fig.update_layout(autosize=False,width=1200,height=600,title='Cost Analysis')
    st.plotly_chart(fig)

    hourly_analysis = dcl_mastercodes[['date', 'mastercode','eff', 'Hourly Throughput', "h_target" ]].rename(columns={'eff':'%Efficiency', 
                                                                                                                 'h_target': 'Hourly Target'}).set_index('date').round(0)
    fig = px.area(hourly_analysis, facet_col="mastercode", facet_col_wrap=4, width = 1300,height=600, title = 'Horuly Operations Analysis')
    st.plotly_chart(fig)

    hourly_analysis_grouped = dcl_mastercodes.groupby(['mastercode'], as_index= False).agg(
                              Efficiency = pd.NamedAgg('eff', aggfunc='mean'),
                              h_throughput = pd.NamedAgg('Hourly Throughput', aggfunc='mean'),
                              h_target = pd.NamedAgg('h_target', aggfunc='mean')
    ).round(0)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Hourly Target", x=hourly_analysis_grouped['mastercode'], y=hourly_analysis_grouped['h_target']))
    fig.add_trace(go.Bar(name="Hourly Throughput", x=hourly_analysis_grouped['mastercode'], y=hourly_analysis_grouped['h_throughput']))
    fig.add_trace(go.Bar(name="% Efficiency", x=hourly_analysis_grouped['mastercode'], y=hourly_analysis_grouped['Efficiency']))
    fig.update_layout(autosize=False,width=1200,height=600,title='Hourly Operations Analysis')
    st.plotly_chart(fig)

    fig = px.scatter_3d(dcl_mastercodes, x='Hourly Throughput', y='cost_variance', z='product_age',
              color='mastercode', width = 1300,height=600, title = '3D Scatter plot for cost analysis')
    st.plotly_chart(fig)
    dcl_mastercodes = dcl_mastercodes.rename(columns={
        'price':'CM', 
        'h_target':'Hourly Target',
        'qty':'Total Output',
        'total_target':'Total Target Output','eff':'Efficiency'
    })
    st.header('Dataset')
    AgGrid(dcl_mastercodes.round(3))
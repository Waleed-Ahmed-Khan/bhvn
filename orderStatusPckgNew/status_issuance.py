import streamlit as st
from common import vizHelper
from st_aggrid import AgGrid
from orderStatusPckg import status_helper
import plotly.express as px
import pandas as pd
import adminPckg.userManagement as userManagement
from static.formatHelper import hover_size


def render_issuance_status(username): 
    st.markdown(hover_size(), unsafe_allow_html=True)
    if st.session_state['selected_po_for_overall_status']:
        customer_po = st.session_state['selected_po_for_overall_status']
        issuance_df = status_helper.get_base_df_for_status('STI', customer_po)
        if len(issuance_df)>0:
            sales_df = status_helper.get_sales_df(customer_po)
            issuance_status = status_helper.dep_wise_status(issuance_df, sales_df)
            issuance_status.drop(columns=['cancel', 'confirm', 'confirmdate'], inplace=True)

            min_date_issuance, max_date_issuance, issuance_leadtime = status_helper.get_dep_status_vars(issuance_df)
            #df_status = 
            st.subheader(f"Issuance status for {customer_po}")
            issuance_status.drop('itemid', axis=1, inplace=True)
            issuance_status['Completion_pct'] = round((issuance_status['qty']/issuance_status['itemqtyorder'])*100, 1)
            issuance_status.rename(columns={'qty':'OutputQty','itemqtyorder':'OrderQty', 'description': 'Article'}, inplace=True)
            issuance_status['Status'] = issuance_status.apply(status_helper.get_status, axis=1)

            if 'Open' in issuance_status['Status'].unique().tolist():
                over_all_status = 'Open'
            else:
                over_all_status = 'Close'

            col1, col2, col3, col4 = st.columns(4)
            with col1: 
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>Issuance Start</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{min_date_issuance}</h4>", unsafe_allow_html= True)
            with col2: 
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>Issuance End</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{max_date_issuance}</h4>", unsafe_allow_html= True)
            with col3:
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>Issuance Status</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{over_all_status}</h4>", unsafe_allow_html= True)
            with col4:
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>Lead time</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{issuance_leadtime} days</h4>", unsafe_allow_html= True)

            col1, col2 = st.columns(2)
            if len(issuance_status)>1 and issuance_status['Article'].nunique()==1:
                issuance_status['Article'] = issuance_status['Article'] + issuance_status['size']
            col1.plotly_chart(vizHelper.stack_or_group_chart_px(issuance_status.sort_values(by='Completion_pct', ascending = True),'Article', 'Completion_pct', color = 'Status' , barmode="stack", orientation="h", height=500, width = 600, color_sequence= ["red", "green"],title="Article wise Issuance", hover_data = ['OrderQty', 'OutputQty']))
            col2.plotly_chart(vizHelper.pie_chart(issuance_status, 'OutputQty', 'Article', hover_name = 'Article', title='Article wise Issuance'))
            st.subheader('Sewing Status Details')
            issuance_status.rename(columns={'OutputQty':'IssuedQty'}, inplace=True)
            AgGrid(issuance_status)
            userManagement.app_logger(username, "Issuance status")


        else:
            st.info(f'Dear {username}, issuance of "{customer_po}" has not yet started')
    else :
        st.info(f"Dear {username}, please check the status in the overall status first, then comeback here again")
import streamlit as st
from common import vizHelper
from st_aggrid import AgGrid
from orderStatusPckg import status_helper
import adminPckg.userManagement as userManagement
from static.formatHelper import hover_size
from orderStatusPckg.status_helper import get_df_for_purchase_status
import pandas as pd
import numpy as np 


def render_purchase_status(username): 
    st.markdown(hover_size(), unsafe_allow_html=True)
    if st.session_state['selected_po_for_overall_status']:
        customer_po = st.session_state['selected_po_for_overall_status']
        purchase_status = get_df_for_purchase_status(customer_po)
        purchase_status.drop_duplicates(keep='first', inplace=True)
        purchase_status.dropna(subset=["Customer PO", "BHVN PO", "Purchase Order #"])
        purchase_status1 = purchase_status.copy()
        purchase_status = purchase_status.drop_duplicates(subset = ['Customer PO', 'BHVN PO', 'Purchase Order #', 'Item Description', 'Order Date', 'Required Date', 'Ordered Qty'], keep = "first")
        cols_to_groupby = ['Customer PO', 'BHVN PO', 'Purchase Order #', 'Item Description', 'Order Date', 'Required Date', 'Ordered Qty', 'Received Qty']
        #purch1 = pd.DataFrame()
        cols_to_groupby_without_receive_qty = ['Customer PO', 'BHVN PO', 'Purchase Order #', 'Item Description', 'Order Date', 'Required Date', 'Ordered Qty']
        purchase_status1 = purchase_status1[cols_to_groupby].groupby(cols_to_groupby_without_receive_qty).agg({"Received Qty":"sum"}).reset_index()
        purchase_status = pd.merge(left= purchase_status, right = purchase_status1, how = 'left', on=cols_to_groupby_without_receive_qty)
        purchase_status.drop(columns=['Received Qty_x'], inplace=True)
        purchase_status.rename(columns={'Received Qty_y':'Received Qty'}, inplace=True)
        del(purchase_status1)

        purchase_status['Order Status'] = np.where(purchase_status['Ordered Qty'] > purchase_status['Received Qty'] ,"Open", "Closed")
             
        if len(purchase_status)>0:
            min_date_purchase, max_date_purchase, purchase_leadtime = status_helper.get_dep_status_vars(purchase_status, purchase=True)
            st.subheader(f"Purchase status for {customer_po}")
            purchase_status['Completion_pct'] = round((purchase_status['Received Qty']/purchase_status['Ordered Qty'])*100, 1)
            
            if 'Open' in purchase_status['Order Status'].unique().tolist():
                over_all_status = 'Open'
            else:
                over_all_status = 'Close'

            col1, col2, col3, col4 = st.columns(4)
            with col1: 
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>Purchase Start</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{min_date_purchase}</h4>", unsafe_allow_html= True)
            with col2: 
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>Purchase End</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{max_date_purchase}</h4>", unsafe_allow_html= True)
            with col3:
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>Purchase Status</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{over_all_status}</h4>", unsafe_allow_html= True)
            with col4:
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>Lead time</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{purchase_leadtime} days</h4>", unsafe_allow_html= True)

            col1, col2 = st.columns(2)
            col1.plotly_chart(vizHelper.stack_or_group_chart_px(purchase_status.sort_values(by='Completion_pct', ascending = True),
                'Item Description', 'Completion_pct', color = 'Order Status' , barmode="stack", orientation="h", height=500, width = 600,
                 color_sequence= ["red", "green"],title="Item wise Purchase status", hover_data = ['Ordered Qty', 'Received Qty']))
            col2.plotly_chart(vizHelper.pie_chart(purchase_status, 'Received Qty', 'Item Description', hover_name = 'Item Description', title='Item wise Purchase ratio'))
            st.subheader('Purchase Status Details')
            AgGrid(purchase_status)
            userManagement.app_logger(username, "Purchase order status")


        else:
            st.info(f'Dear {username}, Purchase of "{customer_po}" has not yet started')
    else :
        st.info(f"Dear {username}, please check the status in the overall status first, then comeback here again")
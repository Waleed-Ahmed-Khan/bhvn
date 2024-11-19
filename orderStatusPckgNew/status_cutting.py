import streamlit as st
from common import vizHelper
from st_aggrid import AgGrid
from orderStatusPckg import status_helper
import adminPckg.userManagement as userManagement
from static.formatHelper import hover_size


def render_cutting_status(username): 
    st.markdown(hover_size(), unsafe_allow_html=True)
    if st.session_state['selected_po_for_overall_status']:
        customer_po = st.session_state['selected_po_for_overall_status']
        cutting_df = status_helper.get_base_df_for_status('CT', customer_po)
        if len(cutting_df)>0:
            sales_df = status_helper.get_sales_df(customer_po)
            cutting_status = status_helper.dep_wise_status(cutting_df, sales_df, item_partwise_for_cutting=True)
            cutting_status.drop(columns=['cancel', 'confirm', 'confirmdate'], inplace=True)

            min_date_cutting, max_date_cutting, cutting_leadtime = status_helper.get_dep_status_vars(cutting_df)
            #df_status = 
            st.subheader(f"Cutting status for {customer_po}")
            cutting_status.drop('itemid', axis=1, inplace=True)
            cutting_status['Completion_pct'] = round((cutting_status['qty']/cutting_status['itemqtyorder'])*100, 1)
            cutting_status.rename(columns={'qty':'OutputQty','itemqtyorder':'OrderQty', 'description': 'Article'}, inplace=True)
            cutting_status['Status'] = cutting_status.apply(status_helper.get_status, axis=1)

            if 'Open' in cutting_status['Status'].unique().tolist():
                over_all_status = 'Open'
            else:
                over_all_status = 'Close'


            col1, col2, col3, col4 = st.columns(4)
            with col1: 
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>Cutting Start</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{min_date_cutting}</h4>", unsafe_allow_html= True)
            with col2: 
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>Cutting End</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{max_date_cutting}</h4>", unsafe_allow_html= True)
            with col3:
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>Cutting Status</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{over_all_status}</h4>", unsafe_allow_html= True)
            with col4:
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>Lead time</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{cutting_leadtime} days</h4>", unsafe_allow_html= True)

            col1, col2 = st.columns(2)
            if len(cutting_status)>1 and cutting_status['Article'].nunique()==1:
                cutting_status['Article'] = cutting_status['Article'] + cutting_status['size']

            col1.plotly_chart(vizHelper.stack_or_group_chart_px(cutting_status.sort_values(by='Completion_pct', ascending = True),'Article', 'Completion_pct', color = 'Status' , barmode="stack", orientation="h", height=500, width = 600, color_sequence= ["red", "green"],title="Article wise Cutting status", hover_data = ['OrderQty', 'OutputQty']))
            col2.plotly_chart(vizHelper.pie_chart(cutting_status, 'OutputQty', 'Article', hover_name = 'Article', title='Article wise output/cutting ratio'))
            st.subheader('Cutting Status Details')
            AgGrid(cutting_status)
            userManagement.app_logger(username, "Cutting order status")


        else:
            st.info(f'Dear {username}, Cutting of "{customer_po}" has not yet started')
    else :
        st.info(f"Dear {username}, please check the status in the overall status first, then comeback here again")
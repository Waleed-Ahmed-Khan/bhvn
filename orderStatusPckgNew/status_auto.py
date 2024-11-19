import streamlit as st
from common import vizHelper
from st_aggrid import AgGrid
from orderStatusPckg import status_helper
import adminPckg.userManagement as userManagement
from static.formatHelper import hover_size


def render_auto_status(username): 
    st.markdown(hover_size(), unsafe_allow_html=True)
    if st.session_state['selected_po_for_overall_status']:
        customer_po = st.session_state['selected_po_for_overall_status']
        auto_df = status_helper.get_base_df_for_status('AT', customer_po)
        if len(auto_df)>0:
            sales_df = status_helper.get_sales_df(customer_po)
            auto_status = status_helper.dep_wise_status(auto_df, sales_df)
            auto_status.drop(columns=['cancel', 'confirm', 'confirmdate'], inplace=True)

            min_date_auto, max_date_auto, auto_leadtime = status_helper.get_dep_status_vars(auto_df)
            #df_status = 
            st.subheader(f"Automation status for {customer_po}")
            auto_status.drop('itemid', axis=1, inplace=True)
            auto_status['Completion_pct'] = round((auto_status['qty']/auto_status['itemqtyorder'])*100, 1)
            auto_status.rename(columns={'qty':'OutputQty','itemqtyorder':'OrderQty', 'description': 'Article'}, inplace=True)
            auto_status['Status'] = auto_status.apply(status_helper.get_status, axis=1)

            if 'Open' in auto_status['Status'].unique().tolist():
                over_all_status = 'Open'
            else:
                over_all_status = 'Close'

            col1, col2, col3, col4 = st.columns(4)
            with col1: 
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>Automation Start</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{min_date_auto}</h4>", unsafe_allow_html= True)
            with col2: 
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>Automation End</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{max_date_auto}</h4>", unsafe_allow_html= True)
            with col3:
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>Automation Status</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{over_all_status}</h4>", unsafe_allow_html= True)
            with col4:
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>Lead time</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{auto_leadtime} days</h4>", unsafe_allow_html= True)

            col1, col2 = st.columns(2)
            if len(auto_status)>1 and auto_status['Article'].nunique()==1:
                auto_status['Article'] = auto_status['Article'] + auto_status['size']
            col1.plotly_chart(vizHelper.stack_or_group_chart_px(auto_status.sort_values(by='Completion_pct', ascending = True),'Article', 'Completion_pct', color = 'Status' , barmode="stack", orientation="h", height=500, width = 600, color_sequence= ["red", "green"],title="Article wise Automation status", hover_data = ['OrderQty', 'OutputQty']))
            col2.plotly_chart(vizHelper.pie_chart(auto_status, 'OutputQty', 'Article', hover_name = 'Article', title='Article wise output/production ratio'))
            st.subheader('Automation Status Details')
            AgGrid(auto_status)
            userManagement.app_logger(username, "Automation order status")


        else:
            st.info(f'Dear {username}, Automation of "{customer_po}" has not yet started')
    else :
        st.info(f"Dear {username}, please check the status in the overall status first, then comeback here again")
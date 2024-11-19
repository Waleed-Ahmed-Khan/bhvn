import streamlit as st
from common import vizHelper
from st_aggrid import AgGrid
from orderStatusPckg import status_helper
import adminPckg.userManagement as userManagement
from static.formatHelper import hover_size


def render_packing_status(username): 
    st.markdown(hover_size(), unsafe_allow_html=True)
    if st.session_state['selected_po_for_overall_status']:
        customer_po = st.session_state['selected_po_for_overall_status']
        packing_df = status_helper.get_base_df_for_status('RFP', customer_po)
        if len(packing_df)>0:
            sales_df = status_helper.get_sales_df(customer_po)
            packing_status = status_helper.dep_wise_status(packing_df, sales_df)
            packing_status.drop(columns=['cancel', 'confirm', 'confirmdate'], inplace=True)

            min_date_packing, max_date_packing, packing_leadtime = status_helper.get_dep_status_vars(packing_df)
            #df_status = 
            st.subheader(f"Packing status for {customer_po}")
            packing_status.drop('itemid', axis=1, inplace=True)
            packing_status['Completion_pct'] = round((packing_status['qty']/packing_status['itemqtyorder'])*100, 1)
            packing_status.rename(columns={'qty':'OutputQty','itemqtyorder':'OrderQty', 'description': 'Article'}, inplace=True)
            packing_status['Status'] = packing_status.apply(status_helper.get_status, axis=1)

            
            if 'Open' in packing_status['Status'].unique().tolist():
                over_all_status = 'Open'
            else:
                over_all_status = 'Close'

            col1, col2, col3, col4 = st.columns(4)
            with col1: 
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>Packing Start</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{min_date_packing}</h4>", unsafe_allow_html= True)
            with col2: 
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>Packing End</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{max_date_packing}</h4>", unsafe_allow_html= True)
            with col3:
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>Packing Status</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{over_all_status}</h4>", unsafe_allow_html= True)
            with col4:
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>Lead time</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{packing_leadtime} days</h4>", unsafe_allow_html= True)

            col1, col2 = st.columns(2)
            if len(packing_status)>1 and packing_status['Article'].nunique()==1:
                packing_status['Article'] = packing_status['Article'] + packing_status['size']
            col1.plotly_chart(vizHelper.stack_or_group_chart_px(packing_status.sort_values(by='Completion_pct', ascending = True),'Article', 'Completion_pct', color = 'Status' , barmode="stack", orientation="h", height=500, width = 600, color_sequence= ["red", "green"],title="Article wise Packing status", hover_data = ['OrderQty', 'OutputQty']))
            col2.plotly_chart(vizHelper.pie_chart(packing_status, 'OutputQty', 'Article', hover_name = 'Article', title='Article wise output/production ratio'))
            st.subheader('Packing Status Details')
            AgGrid(packing_status)
            userManagement.app_logger(username, "Packing order status")


        else:
            st.info(f'Dear {username}, Packing of "{customer_po}" has not yet started')
    else :
        st.info(f"Dear {username}, please check the status in the overall status first, then comeback here again")
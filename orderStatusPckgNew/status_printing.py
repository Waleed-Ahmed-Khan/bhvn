import streamlit as st
from common import vizHelper
from st_aggrid import AgGrid
from orderStatusPckg import status_helper
import adminPckg.userManagement as userManagement
from static.formatHelper import hover_size


def render_printing_status(username): 
    st.markdown(hover_size(), unsafe_allow_html=True)
    if st.session_state['selected_po_for_overall_status']:
        customer_po = st.session_state['selected_po_for_overall_status']
        printing_df = status_helper.get_base_df_for_status('CT', customer_po)
        if len(printing_df)>0:
            sales_df = status_helper.get_sales_df(customer_po)
            printing_status = status_helper.dep_wise_status(printing_df, sales_df, item_partwise_for_cutting=True)
            printing_status.drop(columns=['cancel', 'confirm', 'confirmdate'], inplace=True)

            min_date_printing, max_date_printing, printing_leadtime = status_helper.get_dep_status_vars(printing_df)
            #df_status = 
            st.subheader(f"Printing status for {customer_po}")
            printing_status.drop('itemid', axis=1, inplace=True)
            printing_status['Completion_pct'] = round((printing_status['qty']/printing_status['itemqtyorder'])*100, 1)
            printing_status.rename(columns={'qty':'OutputQty','itemqtyorder':'OrderQty', 'description': 'Article'}, inplace=True)
            printing_status['Status'] = printing_status.apply(status_helper.get_status, axis=1)

            if 'Open' in printing_status['Status'].unique().tolist():
                over_all_status = 'Open'
            else:
                over_all_status = 'Close'


            col1, col2, col3, col4 = st.columns(4)
            with col1: 
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>Printing Start</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{min_date_printing}</h4>", unsafe_allow_html= True)
            with col2: 
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>Printing End</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{max_date_printing}</h4>", unsafe_allow_html= True)
            with col3:
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>Printing Status</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{over_all_status}</h4>", unsafe_allow_html= True)
            with col4:
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>Lead time</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{printing_leadtime} days</h4>", unsafe_allow_html= True)

            col1, col2 = st.columns(2)
            if len(printing_status)>1 and printing_status['Article'].nunique()==1:
                printing_status['Article'] = printing_status['Article'] + printing_status['size']

            col1.plotly_chart(vizHelper.stack_or_group_chart_px(printing_status.sort_values(by='Completion_pct', ascending = True),'Article', 'Completion_pct', color = 'Status' , barmode="stack", orientation="h", height=500, width = 600, color_sequence= ["red", "green"],title="Article wise Printing status", hover_data = ['OrderQty', 'OutputQty']))
            col2.plotly_chart(vizHelper.pie_chart(printing_status, 'OutputQty', 'Article', hover_name = 'Article', title='Article wise output/printing ratio'))
            st.subheader('Printing Status Details')
            AgGrid(printing_status)
            userManagement.app_logger(username, "Printing order status")


        else:
            st.info(f'Dear {username}, Printing of "{customer_po}" has not yet started')
    else :
        st.info(f"Dear {username}, please check the status in the overall status first, then comeback here again")
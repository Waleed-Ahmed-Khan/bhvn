import streamlit as st
from common import vizHelper
from st_aggrid import AgGrid
from orderStatusPckg import status_helper
import adminPckg.userManagement as userManagement
from static.formatHelper import hover_size


def render_final_inspection_status(username):
    st.markdown(hover_size(), unsafe_allow_html=True)
    if st.session_state['selected_po_for_overall_status']:
        customer_po = st.session_state['selected_po_for_overall_status']
        inspection_df = status_helper.get_base_df_for_status('FIN', customer_po)
        if len(inspection_df)>0:
            sales_df = status_helper.get_sales_df(customer_po)
            inspection_status = status_helper.dep_wise_status(inspection_df, sales_df)
            inspection_status.drop(columns=['cancel', 'confirm', 'confirmdate'], inplace=True)

            min_date_inspection, max_date_inspection, inspection_leadtime = status_helper.get_dep_status_vars(inspection_df)
            #df_status = 
            st.subheader(f"Final Inspection status for {customer_po}")
            inspection_status.drop('itemid', axis=1, inplace=True)
            inspection_status['Completion_pct'] = round((inspection_status['qty']/inspection_status['itemqtyorder'])*100, 1)
            inspection_status.rename(columns={'qty':'OutputQty','itemqtyorder':'OrderQty', 'description': 'Article'}, inplace=True)
            inspection_status['Status'] = inspection_status.apply(status_helper.get_status, axis=1)

            if 'Open' in inspection_status['Status'].unique().tolist():
                over_all_status = 'Open'
            else:
                over_all_status = 'Close'

            col1, col2, col3, col4 = st.columns(4)
            with col1: 
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>Inspection Start</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{min_date_inspection}</h4>", unsafe_allow_html= True)
            with col2: 
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>Inspection End</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{max_date_inspection}</h4>", unsafe_allow_html= True)
            with col3:
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>Inspection Status</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{over_all_status}</h4>", unsafe_allow_html= True)
            with col4:
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>Lead time</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{inspection_leadtime} days</h4>", unsafe_allow_html= True)

            col1, col2 = st.columns(2)
            if len(inspection_status)>1 and inspection_status['Article'].nunique()==1:
                inspection_status['Article'] = inspection_status['Article'] + inspection_status['size']
            col1.plotly_chart(vizHelper.stack_or_group_chart_px(inspection_status.sort_values(by='Completion_pct', ascending = True),'Article', 'Completion_pct', color = 'Status' , barmode="stack", orientation="h", height=500, width = 600, color_sequence= ["red", "green"],title="Article wise Final Inspection", hover_data = ['OrderQty', 'OutputQty']))
            col2.plotly_chart(vizHelper.pie_chart(inspection_status, 'OutputQty', 'Article', hover_name = 'Article', title='Article wise output/inspection ratio'))
            st.subheader('Final Inspection Status Details')
            AgGrid(inspection_status)
            userManagement.app_logger(username, "Final Inspection status")


        else:
            st.info(f'Dear {username}, Final Inspection of "{customer_po}" has not yet started')
    else :
        st.info(f"Dear {username}, please check the status in the overall status first, then comeback here again")
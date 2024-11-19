import pandas as pd  
import streamlit as st
from common import helper, vizHelper
import adminPckg.userManagement as userManagement
import static.formatHelper as fh
from st_aggrid import AgGrid

def render_cutting(username):
    st.header('Cutting Dashboard')
    st.write(fh.format_st_button(), unsafe_allow_html=True)
    cutting_df_query = "SELECT * FROM cutting_pro5"
    cutting_qc_query = "SELECT * FROM cutting_qc2"
    cutting_df = helper.load_data(cutting_df_query)
    cutting_df = cutting_df.astype({'section': 'object', 'itemid':'object', 'partid':'object', 'qty':'float'})
    cutting_qc = helper.load_data(cutting_qc_query)
    cutting_df = cutting_df.drop_duplicates(keep='first')
    cutting_qc = cutting_qc.drop_duplicates(keep='first')
    
    date = cutting_df['date'].unique().tolist()
    cutting_df_pos = cutting_df.customer_PO.unique().tolist()
    cutting_qc_pos = cutting_qc.Customer_PO.unique().tolist()
    all_pos =  cutting_df_pos + cutting_qc_pos 
    all_pos.insert(0, "All POs")
    cutting_qc_opr = cutting_qc.opr_code.unique().tolist()
    cutting_df_opr = cutting_df.opr_code.unique().tolist()
    all_opr_codes = cutting_qc_opr + cutting_df_opr 
    all_opr_codes.insert(0, "All Operators")
    with st.form(key="cutting_form"):
        col1, col2, col3 =  st.columns(3)
        with col1:
            st.markdown("**Cutting Date :**")
            date_selection = st.slider('',min_value=min(date), max_value=max(date), value=(min(date),max(date))) 
        with col2:
            st.markdown("**Purchase Order :**")
            po_selection = st.multiselect('',  all_pos, default='All POs')
        with col3:
            st.markdown("**Operator Code :**")
            opr_selection = st.multiselect('',  all_opr_codes, default='All Operators')
        st.markdown('<hr/>', unsafe_allow_html = True)
        st.form_submit_button(label = "📈 Build Dashboard")

    if po_selection ==["All POs"]:
        customer_po_list = all_pos
        
        po_selection = customer_po_list
    else:
        if 'All POs' in po_selection:
            po_selection.pop(0)
    if opr_selection ==['All Operators']:
        opr_code_list = all_opr_codes
        opr_selection = opr_code_list
    else:
        if 'All Operators' in opr_selection:
            opr_selection.pop(0)
    pie_bar_defect_type_qc, pie_bar_opr_code_qc, cutting_df = helper.preprocess_cutting(cutting_qc, cutting_df, date_selection, po_selection, opr_selection)
    if isinstance (pie_bar_defect_type_qc, pd.DataFrame):
        kpi1, kpi2,kpi3 =  st.columns(3)
        with kpi1:
            st.markdown(f"<h4 style = 'text-align: center; color: red;'>Total Defects</h4>", unsafe_allow_html= True)
            st.markdown(f"<h3 style = 'text-align: center; color: blue;'>{pie_bar_defect_type_qc['defectQty'].sum()}</h3>", unsafe_allow_html= True)

        with kpi2:
            st.markdown(f"<h4 style = 'text-align: center; color: red;'>Total Production</h3>", unsafe_allow_html= True)
            st.markdown(f"<h3 style = 'text-align: center; color: blue;'>{int(cutting_df.qty.sum())}</h1>", unsafe_allow_html= True)

        with kpi3:
            st.markdown(f"<h4 style = 'text-align: center; color: red;'>Defect Rate</h4>", unsafe_allow_html= True)
            st.markdown(f"<h3 style = 'text-align: center; color: blue;'>{round((pie_bar_defect_type_qc['defectQty'].sum()/cutting_df.qty.sum())*100, 4)} %</h3>", unsafe_allow_html= True)
        st.markdown('<hr/>', unsafe_allow_html = True)
        col1, col2 = st.columns(2)
        col1.plotly_chart(vizHelper.barchart(pie_bar_defect_type_qc, 'defectQty', 'defect_type', title='Defect Type wise count of Defect'))
        col2.plotly_chart(vizHelper.pie_chart(pie_bar_defect_type_qc, 'defectQty', 'defect_type', title='Defect Type wise percent Defect'))
        st.markdown('<hr/>', unsafe_allow_html = True)
        col1, col2 = st.columns(2)
        col1.plotly_chart(vizHelper.barchart(pie_bar_opr_code_qc, 'defectQty', 'opr_code', title='Operator wise count of Defect'))
        col2.plotly_chart(vizHelper.pie_chart(pie_bar_opr_code_qc, 'defectQty', 'opr_code', title=' Operator wise percent Defect'))
        st.markdown('<hr/>', unsafe_allow_html = True)
        st.subheader('Cutting Data')
        cutting_df = cutting_df[(cutting_df['customer_PO'].isin(po_selection)) & (cutting_df['opr_code'].isin(opr_selection))]
        AgGrid(cutting_df)
        df_xlsx = helper.to_excel(cutting_df)
        st.download_button(label='📥 Download Dataset',
                            data=df_xlsx ,
                            file_name= 'CuttingData.xlsx')

        st.markdown('<hr/>', unsafe_allow_html = True)
        st.subheader('Quality Data')
        cutting_qc = cutting_qc[(cutting_qc['Customer_PO'].isin(po_selection)) & (cutting_qc['opr_code'].isin(opr_selection))]
        AgGrid(cutting_qc)
        df_xlsx = helper.to_excel(cutting_qc)
        st.download_button(label='📥 Download Dataset',
                            data=df_xlsx ,
                            file_name= 'CuttingQCData.xlsx')
        userManagement.app_logger(username, "Cutting Operations")

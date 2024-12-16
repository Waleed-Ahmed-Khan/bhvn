import pandas as pd  
import streamlit as st
from common import helper, vizHelper
import adminPckg.userManagement as userManagement
import static.formatHelper as fh
from st_aggrid import AgGrid
import plotly.express as px


def render_cutting(username):
    st.header('Cutting Dashboard')
    st.write(fh.format_st_button(), unsafe_allow_html=True)
    cutting_df_query = "SELECT * FROM cutting_pro5"
    cutting_qc_query = "SELECT * FROM cutting_qc2"

    #SELECT * FROM `tblcuttingdefects_quantity` having these fields id 	date 	dept_id 	section_id 	TotalQty 	orderno 	ProductionNo 	ponumber 	TotalDefectQty 	TotalPassedQty 	itemid 	
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
    cutting_df_sec = cutting_df.section.unique().tolist()
    cutting_df_sec.insert(0, "All Sections")
    cutting_qc_opr = cutting_qc.opr_code.unique().tolist()
    cutting_df_opr = cutting_df.opr_code.unique().tolist()
    all_opr_codes = cutting_qc_opr + cutting_df_opr 
    all_opr_codes.insert(0, "All Operators")
    with st.form(key="cutting_form"):
        col1, col2, col3, col4 =  st.columns(4)
        with col1:
            st.markdown("**Cutting Date :**")
            date_selection = st.slider('',min_value=min(date), max_value=max(date), value=(min(date),max(date))) 
        with col2:
            st.markdown("**Purchase Order :**")
            po_selection = st.multiselect('',  all_pos, default='All POs')
        with col3:
            st.markdown("**Operator Code :**")
            opr_selection = st.multiselect('',  all_opr_codes, default='All Operators')
        with col4:
            st.markdown("**Sections Code :**")
            sec_selection = st.multiselect('',  cutting_df_sec, default='All Sections')
            
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
    if sec_selection ==['All Sections']:
        sec_code_list = cutting_df_sec
        sec_selection = sec_code_list
    else:
        if 'All Sections' in sec_selection:
            sec_selection.pop(0)
    pie_bar_defect_type_qc, pie_bar_opr_code_qc, cutting_df, yield_percentage, format_defect_density, defect_per_million, avg_production_per_opr, section_production, avg_production_per_sec = helper.preprocess_cutting(
    cutting_qc, cutting_df, date_selection, po_selection, opr_selection, sec_selection)

    if isinstance(pie_bar_defect_type_qc, pd.DataFrame):
        kpi1, kpi2, kpi3, Kpi4= st.columns(4)
    
        with kpi1:
            st.markdown(f"<h4 style='text-align: center; color: red;'>Total Defects</h4>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='text-align: center; color: blue;'>{pie_bar_defect_type_qc['defectQty'].sum()}</h3>", unsafe_allow_html=True)

        with kpi2:
            st.markdown(f"<h4 style='text-align: center; color: red;'>Total Production</h4>", unsafe_allow_html=True)
            total_production = cutting_df['qty'].sum()  # Calculate total production directly from cutting_df
            st.markdown(f"<h3 style='text-align: center; color: blue;'>{int(total_production)}</h3>", unsafe_allow_html=True)

        with kpi3:
            st.markdown(f"<h4 style='text-align: center; color: red;'>Defect Rate</h4>", unsafe_allow_html=True)
            defect_rate = (pie_bar_defect_type_qc['defectQty'].sum() / total_production) * 100 if total_production > 0 else 0
            st.markdown(f"<h3 style='text-align: center; color: blue;'>{round(defect_rate, 4)}%</h3>", unsafe_allow_html=True)


        with Kpi4:
            st.markdown(f"<h4 style='text-align: center; color: red;'>Avg Production per Section</h4>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='text-align: center; color: blue;'>{round(avg_production_per_sec, 2)}</h3>", unsafe_allow_html=True)
      
        
        st.markdown('<hr/>', unsafe_allow_html = True)
        kpi1, kpi2, kpi3, Kpi4 = st.columns(4)
        with kpi1:
            st.markdown(f"<h4 style='text-align: center; color: red;'>Yield</h4>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='text-align: center; color: blue;'>{round(yield_percentage, 6)}%</h3>", unsafe_allow_html=True)
            with st.expander("Yield Formula"):
                st.latex(r'''
                   = \frac{Total\ Production - Total\ Defects}{Total\ Production} \times 100\%
                    ''')

        with kpi2:
            st.markdown(f"<h4 style='text-align: center; color: red;'>Defect Density</h4>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='text-align: center; color: blue;'>"f"{format_defect_density}(Standard)""</h3>", unsafe_allow_html=True)
            with st.expander("Density Rate Formula"):
                st.latex(r'''
                    Defect\ Density = \frac{Total \ Defect}{Total \ Production}
                    ''')

        with kpi3:
            st.markdown(f"<h4 style='text-align: center; color: red;'>Avg Production per Operator</h4>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='text-align: center; color: blue;'>{round(avg_production_per_opr, 2)}</h3>", unsafe_allow_html=True)
            with st.expander("Average Production per Operator Formula"):
                st.latex(r'''
                    = \frac{\text{Total Production}}{\text{Number of Operators}}
                    ''')
                
        with Kpi4:
            st.markdown(f"<h4 style='text-align: center; color: red;'>Defect Per Million</h4>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='text-align: center; color: blue;'>{defect_per_million}</h3>", unsafe_allow_html=True)
            with st.expander("Defect Per Million Formula"):
                st.latex(r'''
                    \text{Defects Per Million} = \text{Defect Density} \times 10^6
                    ''')


     

        st.markdown('<hr/>', unsafe_allow_html = True)

        col1, col2 = st.columns(2)
        col1.plotly_chart(vizHelper.barchart(pie_bar_defect_type_qc, 'defectQty', 'defect_type', title='Defect Type wise count of Defect'))
        col2.plotly_chart(vizHelper.pie_chart(pie_bar_defect_type_qc, 'defectQty', 'defect_type', title='Defect Type wise percent Defect'))
        st.markdown('<hr/>', unsafe_allow_html = True)
        # Section-wise Production Graphs
       
    
        # Create columns for layout
        col1, col2 = st.columns(2)

        # Bar Chart for Section-wise Production
        col1.plotly_chart(vizHelper.barchart(
            section_production,
            'qty',            # Total production as y-axis value
            'section',        # Section as x-axis labels
            title='Section-wise Total Production'
        ))

        # Pie Chart for Section-wise Percent Production
        col2.plotly_chart(vizHelper.pie_chart(
            section_production,
            'qty',            # Total production as metric
            'section',        # Section as labels
            title='Section-wise Percent Production',
            
        ))
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

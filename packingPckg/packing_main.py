import streamlit as st
from common import helper, vizHelper
import packingPckg.packing as packing, adminPckg.userManagement as userManagement
import pandas as pd
import plotly.graph_objects as go
import static.formatHelper as fh
from st_aggrid import AgGrid
from static.formatHelper import hover_size
from packingPckg.packing_helper import preprocess_packing, preprocess_packing_lastworking


def render_packing_operations(username):
    st.markdown(hover_size(), unsafe_allow_html=True)
    st.write(fh.format_st_button(), unsafe_allow_html=True)
    with st.spinner("Packing Dashboard is Getting Ready for you... 🎁"):
        complete_df = packing.get_complete_packing_data()
    date = complete_df['date'].unique().tolist()
    year = complete_df['year'].unique().tolist()
    year = year[::-1] # reverse the list for ['current_year', 2021]
    customer_pos = complete_df.customer_PO.unique().tolist()
    customer_pos.insert(0, 'All POs')   
    customer = complete_df['SubCategory'].unique().tolist()
    customer.insert(0, 'All Customers')

    complete_df['overtime']  = complete_df['overtime_hours'].apply(lambda x : "No" if x == 0 or pd.isnull(x) else "Yes")
    overtime_list = complete_df['overtime'].unique().tolist()
    overtime_list.insert(0, 'Total Time')
    mastercode = complete_df['mastercode'].unique().tolist()
    mastercode.insert(0, 'All Master Codes')
    size = complete_df['size'].unique().tolist()
    size.insert(0, 'All Sizes')

    with st.form(key = "packing_form"):
        col1, col2, col3, col4 =  st.columns(4)
        with col1:
            st.markdown("**Start Date :**")
            start_date = st.date_input('', pd.to_datetime(min(date)))
        with col2:
            st.markdown("**End Date :**")
            end_date = st.date_input('', pd.to_datetime(max(date)))
            #date_selection = st.slider('',min_value=min(date), max_value=max(date), value=(min(date),max(date))) 
        with col3:
            st.markdown("**Customer PO :**")
            po_selection = st.multiselect('',  customer_pos, default='All POs')
        with col4:
            st.markdown("**Customer :**")
            customer_selection = st.multiselect('',  customer, default='All Customers')

        col1, col2, col3, col4=  st.columns(4)
        with col1:
            st.markdown("**Overtime :**")
            overtime_selection = st.multiselect('',  overtime_list, default='Total Time') 
        with col2:
            st.markdown("**Master Code :**")
            mastercode_selection = st.multiselect('',  mastercode, default='All Master Codes')
        with col3:
            st.markdown("**Size :**")
            size_selection = st.multiselect('',  size, default='All Sizes')
        with col4:
            st.markdown("**Year :**")
            year = st.selectbox('', year)
        st.markdown('<hr/>', unsafe_allow_html = True)
        st.form_submit_button(label = '📈 Build Dashboard')
        
    if po_selection ==["All POs"]:
        customer_po_list = customer_pos
        po_selection = customer_po_list
    if customer_selection ==["All Customers"]:
        customer_list = customer
        customer_selection = customer_list
    if overtime_selection ==["Total Time"]:
        overtime_selection = overtime_list
    if mastercode_selection ==["All Master Codes"]:
        mastercode_list = mastercode
        mastercode_selection = mastercode_list
    if size_selection == ['All Sizes']:
        size_list = size
        size_selection = size_list

    complete_df_t, total_output, total_target, total_co, total_percent_co, avg_efficiency, avg_throughput , sorted_months, co_by_month,eff_by_month, throughput_by_month, customer_wise_eff_thr, customer_qty, co_by_brand = preprocess_packing(
        complete_df, start_date, end_date, year, po_selection, customer_selection, overtime_selection, mastercode_selection, size_selection)
    
    if isinstance (complete_df_t, pd.DataFrame):
        kpi2,kpi3 =  st.columns(2)
        # with kpi1:
        #     st.markdown(f"<h4 style = 'text-align: center; color: red;'>Avg Efficiency</h4>", unsafe_allow_html= True)
        #     st.markdown(f"<h3 style = 'text-align: center; color: blue;'>{round(avg_efficiency, 2)} %</h3>", unsafe_allow_html= True)
        #     with st.expander("Efficiency Formula"):

        #         #st.latex(r"$$Avg Eff = \frac{Σ Efficiency}{Σ Working Days}$$")
        #         st.latex(r'''
        #         =\left(\frac{Σ Output Qty}{Σ Target Qty}\right) * 100
        #         ''')
        with kpi2:
            st.markdown(f"<h4 style = 'text-align: center; color: red;'>Changeover Percentage</h3>", unsafe_allow_html= True)
            st.markdown(f"<h3 style = 'text-align: center; color: blue;'>{int(round(total_percent_co,2))} %</h1>", unsafe_allow_html= True)
            with st.expander("Changeover Percentage Formula"):
                st.latex(r'''
                =\left(\frac{Σ Changeovers}{Σ Executions}\right) * 100
                ''')
        with kpi3:
            st.markdown(f"<h4 style = 'text-align: center; color: red;'>Avg Hourly Throughput</h4>", unsafe_allow_html= True)
            st.markdown(f"<h3 style = 'text-align: center; color: blue;'>{int(avg_throughput)}</h3>", unsafe_allow_html= True)
            with st.expander("Hourly Throughput Formula"):
                st.latex(r'''
                =\left(\frac{Σ Output Qty}{Σ Working Hours}\right)
                ''')
    #st.warning(f"Hi {username.title()}, Please disregard the value of efficiency and target as the API is being migrated, we apologize for any inconvenience caused by the recent database migration. Rest assured, we're working diligently to resolve any issues promptly. Thank you for your patience and understanding.")
    st.markdown('<hr/>', unsafe_allow_html = True)
    col1, col2 = st.columns(2)
    col1.plotly_chart(vizHelper.area_chart(eff_by_month, 'Month', '% Eff','Month', '% Eff', "Month wise Efficiency", unit = "%"))
    col2.plotly_chart(vizHelper.area_chart(throughput_by_month, 'Month', 'Hourly Throughput','Month', 'Hourly Throughput', "Month wise hourly throughput", unit = "/Hr"))
    st.markdown('<hr/>', unsafe_allow_html = True)
    col1, col2 = st.columns(2)
    col1.plotly_chart(vizHelper.area_chart(co_by_month, 'Month', 'percent_co','Month', '% C/O', "Month wise Percentage C/O", unit = "%"))
    col2.plotly_chart(vizHelper.pareto_chart(customer_qty, cat_col='Customer Name', num_col='Quantity', height = 450, width = 600, title='Pareto Chart of Customer wise Production Ratio', y_label = "Production Quantity"))
    st.markdown('<hr/>', unsafe_allow_html = True)
    col1, col2 = st.columns(2)
    #col1.plotly_chart(vizHelper.line_bar(line_wise_eff_thr, x = line_wise_eff_thr['line_number'], y1=line_wise_eff_thr['% Eff'], y2=line_wise_eff_thr['Hourly Throughput'],
    #    legends=['% Eff', 'Hourly Throughput'] ,title='Line wise % Eff and Hourly Throughput' ))
    col1.plotly_chart(vizHelper.pie_chart(co_by_brand, 'C/O','SubCategory', title='Brand wise C/O Ratio' ))
    col2.plotly_chart(vizHelper.line_bar(customer_wise_eff_thr, x = customer_wise_eff_thr['SubCategory'], y1=customer_wise_eff_thr['% Eff'], y2=customer_wise_eff_thr['Hourly Throughput'],
    legends=['% Eff', 'Hourly Throughput'] ,title='Customer wise % Eff and Hourly Throughput' ))
    st.markdown('<hr/>', unsafe_allow_html = True)
    #col1, col2 = st.columns(2)
    
    #col2.plotly_chart(vizHelper.pie_chart(co_by_line, "C/O", 'line_number', title='Line wise C/O Ratio'))

    #st.markdown('<hr/>', unsafe_allow_html = True)
    st.plotly_chart(vizHelper.plot_histogram(complete_df_t, 'Hourly Throughput', 'Hourly Throughput','name','box', ['% Eff', 'C/O'], 'Brand wise Histogram of Hourly Throghput', 1100, 550))
    
    st.markdown('<hr/>', unsafe_allow_html = True)
    st.write('Complete Packing Dataset')
    AgGrid(complete_df_t.drop(columns=['month_no', 'day_no', 'Month','Day', 'unitPrice','name', 'itemcode', 'C/O']))
    # st.download_button(
    # '📥 Download Dataset',complete_df_t.to_csv( index = False ).encode('utf-8'),
    # "SewingData.csv","text/csv",key='download-csv'
    # )
    df_xlsx = helper.to_excel(complete_df_t)
    st.download_button(label='📥 Download Dataset',
                                data=df_xlsx ,
                                file_name= 'PackingData.xlsx')

    userManagement.app_logger(username, "Packing Operations")

def render_recent_working_day(username):
    st.markdown(hover_size(), unsafe_allow_html=True)
    complete_df_for_lwd = packing.get_complete_packing_data()
    recent_day = complete_df_for_lwd['date'].max().strftime("%d %b, %Y")
    complete_df = complete_df_for_lwd[complete_df_for_lwd['date'] == recent_day ]
    complete_df_t, total_output, total_target, total_co, total_percent_co, avg_efficiency, avg_throughput , sorted_months, executions_by_month ,eff_by_month, throughput_by_month, customer_wise_eff_thr, customer_qty, co_by_brand, planned_vs_target = preprocess_packing_lastworking(
        complete_df)
    st.header(f"Last Working Day - {recent_day}")
    if total_target > 0:
        kpi1, kpi2,kpi3 =  st.columns(3)
        with kpi1:
            st.markdown(f"<h4 style = 'text-align: center; color: red;'>Target Quantity</h4>", unsafe_allow_html= True)
            st.markdown(f"<h3 style = 'text-align: center; color: blue;'>{int(total_target)}</h3>", unsafe_allow_html= True)

        with kpi2:
            st.markdown(f"<h4 style = 'text-align: center; color: red;'>Total Output</h3>", unsafe_allow_html= True)
            st.markdown(f"<h3 style = 'text-align: center; color: blue;'>{int(total_output)}</h1>", unsafe_allow_html= True)

        with kpi3:
            st.markdown(f"<h4 style = 'text-align: center; color: red;'>Total C/O</h4>", unsafe_allow_html= True)
            st.markdown(f"<h3 style = 'text-align: center; color: blue;'>{int(total_co)}</h3>", unsafe_allow_html= True)
        st.markdown('<hr/>', unsafe_allow_html = True)
        kpi1, kpi2,kpi3 =  st.columns(3)
        with kpi1:
            st.markdown(f"<h4 style = 'text-align: center; color: red;'>Avg Efficiency</h4>", unsafe_allow_html= True)
            st.markdown(f"<h3 style = 'text-align: center; color: blue;'>{round(avg_efficiency, 2)} %</h3>", unsafe_allow_html= True)

        with kpi2:
            st.markdown(f"<h4 style = 'text-align: center; color: red;'>Percentage Changeover</h3>", unsafe_allow_html= True)
            st.markdown(f"<h3 style = 'text-align: center; color: blue;'>{round(total_percent_co,2)} %</h1>", unsafe_allow_html= True)

        with kpi3:
            st.markdown(f"<h4 style = 'text-align: center; color: red;'>Avg Hourly Throughput</h4>", unsafe_allow_html= True)
            st.markdown(f"<h3 style = 'text-align: center; color: blue;'>{round(avg_throughput, 0)}</h3>", unsafe_allow_html= True)
        st.markdown('<hr/>', unsafe_allow_html = True)
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Actual", x=planned_vs_target['mastercode'], y=planned_vs_target['Output']))
        fig.add_trace(go.Bar(name="Target", x=planned_vs_target['mastercode'], y=planned_vs_target['Target']))
        fig.update_layout(autosize=False,width=1100,height=500,title='Target Vs Actual')
        st.plotly_chart(fig)
        st.markdown('<hr/>', unsafe_allow_html = True)
        col1, col2 = st.columns(2)
        col1.plotly_chart(vizHelper.line_bar(customer_wise_eff_thr, x = customer_wise_eff_thr['SubCategory'], y1=customer_wise_eff_thr['% Eff'], y2=customer_wise_eff_thr['Hourly Throughput'],
        legends=['% Eff', 'Hourly Throughput'] ,title='Brand wise % Eff and Hourly Throughput' ))
        col2.plotly_chart(vizHelper.pie_chart(co_by_brand, "C/O", 'SubCategory', title='Brand wise C/O Ratio'))
        st.markdown('<hr/>', unsafe_allow_html = True)
        st.write('Download Dataset')
        AgGrid(complete_df_t.drop(columns=['month_no', 'day_no', 'Month','Day', 'unitPrice','SubCategory', 'itemcode', 'C/O']))
        # st.download_button(
        # '📥 Download Dataset',complete_df_t.to_csv( index = False ).encode('utf-8'),
        # "SewingData.csv","text/csv",key='download-csv'
        # )
        df_xlsx = helper.to_excel(complete_df_t)
        st.download_button(label='📥 Download Dataset',
                                    data=df_xlsx ,
                                    file_name= 'PackingData.xlsx')
        userManagement.app_logger(username, "Packing LWD")
    else :
        st.write('The "Last Working Day" data is not available for the selection you made, please contact admin if the problem persists, Thank you!')
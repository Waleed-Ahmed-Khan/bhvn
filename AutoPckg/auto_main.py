import streamlit as st
from common import helper, vizHelper
import AutoPckg.auto as auto, adminPckg.userManagement as userManagement
import pandas as pd
import plotly.graph_objects as go
import static.formatHelper as fh
from st_aggrid import AgGrid
from static.formatHelper import hover_size


def render_auto_operations(username):
    st.write(fh.format_st_button(), unsafe_allow_html=True)
    st.markdown(hover_size(), unsafe_allow_html=True)
    with st.spinner("Automation Dashboard is Getting Ready ... ⚙️"):
        complete_df = auto.get_complete_auto_data()
    date = complete_df['date'].unique().tolist()
    year = complete_df['year'].unique().tolist()
    customer_pos = complete_df.customer_PO.unique().tolist()
    customer_pos.insert(0, 'All POs')   
    customer = complete_df['name'].unique().tolist()
    customer.insert(0, 'All Customers')
    opr_code = complete_df['opr_code'].unique().tolist()
    opr_code.insert(0, 'All Operators')
    mastercode = complete_df['mastercode'].unique().tolist()
    mastercode.insert(0, 'All Master Codes')
    size = complete_df['size'].unique().tolist()
    size.insert(0, 'All Sizes')
    with st.form(key='auto_form'):
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
            st.markdown("**Operator Code :**")
            opr_selection = st.multiselect('',  opr_code, default='All Operators') 
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
        st.form_submit_button('📈 Build Dashboard')

    if po_selection ==["All POs"]:
        customer_po_list = customer_pos
        po_selection = customer_po_list
    if customer_selection ==["All Customers"]:
        customer_list = customer
        customer_selection = customer_list
    if opr_selection ==["All Operators"]:
        opr_list = opr_code
        opr_selection = opr_list
    if mastercode_selection ==["All Master Codes"]:
        mastercode_list = mastercode
        mastercode_selection = mastercode_list
    if size_selection == ['All Sizes']:
        size_list = size
        size_selection = size_list
    complete_df_t, total_output, total_target, total_co, total_percent_co, avg_efficiency, avg_throughput , sorted_months, co_by_month,eff_by_month, throughput_by_month, customer_wise_eff_thr, line_wise_eff_thr, customer_qty, co_by_brand, co_by_line = helper.preprocess_auto(
        complete_df, start_date, end_date, year, po_selection, customer_selection, opr_selection, mastercode_selection, size_selection)
    if isinstance (complete_df_t, pd.DataFrame) and len(complete_df_t) > 0:
        kpi1, kpi2,kpi3 =  st.columns(3)
        with kpi1:
            st.markdown(f"<h4 style = 'text-align: center; color: red;'>Avg Efficiency</h4>", unsafe_allow_html= True)
            st.markdown(f"<h3 style = 'text-align: center; color: blue;'>{round(avg_efficiency, 2)} %</h3>", unsafe_allow_html= True)
            with st.expander("Efficiency Formula"):

                #st.latex(r"$$Avg Eff = \frac{Σ Efficiency}{Σ Working Days}$$")
                st.latex(r'''
                =\left(\frac{Σ Output Qty}{Σ Target Qty}\right) * 100
                ''')
        with kpi2:
            st.markdown(f"<h4 style = 'text-align: center; color: red;'>Changeover Percentage</h3>", unsafe_allow_html= True)
            st.markdown(f"<h3 style = 'text-align: center; color: blue;'>{round(total_percent_co,2)} %</h1>", unsafe_allow_html= True)
            with st.expander("Changeover Percentage Formula"):
                st.latex(r'''
                =\left(\frac{Σ Changeovers}{Σ Executions}\right) * 100
                ''')
        with kpi3:
            st.markdown(f"<h4 style = 'text-align: center; color: red;'>Avg Hourly Throughput</h4>", unsafe_allow_html= True)
            st.markdown(f"<h3 style = 'text-align: center; color: blue;'>{int(avg_throughput)} Pairs/Hour</h3>", unsafe_allow_html= True)
            with st.expander("Hourly Throughput Formula"):
                st.latex(r'''
                =\left(\frac{Σ Output Qty}{Σ Working Hours}\right)
                ''')
        
        st.markdown('<hr/>', unsafe_allow_html = True)
        col1, col2 = st.columns(2)
        col1.plotly_chart(vizHelper.area_chart(eff_by_month, 'Month', '% Eff','Month', '% Eff', "Month wise Efficiency", unit = "%"))
        col2.plotly_chart(vizHelper.area_chart(throughput_by_month, 'Month', 'Hourly Throughput','Month', 'Hourly Throughput', "Month wise hourly throughput", unit = "/Hr"))
        st.markdown('<hr/>', unsafe_allow_html = True)
        col1, col2 = st.columns(2)
        col1.plotly_chart(vizHelper.area_chart(co_by_month, 'Month', 'percent_co','Month', '% C/O', "Month wise Percentage C/O"))
        col2.plotly_chart(vizHelper.pie_chart(customer_qty, 'Quantity', 'Customer Name', title='Customer wise Production Ratio'))
        st.markdown('<hr/>', unsafe_allow_html = True)
        col1, col2 = st.columns(2)
        col1.plotly_chart(vizHelper.line_bar(line_wise_eff_thr, x = line_wise_eff_thr['opr_code'], y1=line_wise_eff_thr['% Eff'], y2=line_wise_eff_thr['Hourly Throughput'],
        legends=['% Eff', 'Hourly Throughput'] ,title='Operator wise % Eff and Hourly Throughput' ))
        col2.plotly_chart(vizHelper.line_bar(customer_wise_eff_thr, x = customer_wise_eff_thr['SubCategory'], y1=customer_wise_eff_thr['% Eff'], y2=customer_wise_eff_thr['Hourly Throughput'],
        legends=['% Eff', 'Hourly Throughput'] ,title='Customer wise % Eff and Hourly Throughput' ))
        col1, col2 = st.columns(2)
        fig = vizHelper.heatmap(complete_df_t, 'opr_code', 'machine','% DR', 'mean', 'Machine', 'Operator Code', 'Avg Defect Rate', 'Avg Defect Rate by Operator and Machine')
        col1.plotly_chart(fig)
        fig = vizHelper.heatmap(complete_df_t, 'opr_code', 'machine','Hourly Throughput', 'mean', 'Machine', 'Operator Code', 'Avg Hourly Throughput', 'Avg Hourly Throughput by Operator and Machine')
        col2.plotly_chart(fig)
        st.markdown('<hr/>', unsafe_allow_html = True)
        col1, col2 = st.columns(2)
        col1.plotly_chart(vizHelper.pie_chart(co_by_brand, 'C/O','SubCategory', title='Brand wise C/O Ratio' ))
        complete_df_t[['opr_code', 'machine' ]] = complete_df_t[['opr_code', 'machine' ]].astype(str)
        col2.plotly_chart(vizHelper.multivar_bubble(complete_df_t, 'opr_code', 'machine','ms_hours', 'qty', 'sum', 'opr_code', 'Operator Code', 'Machine Downtime(hrs)', 'machine', 'Sum of Machine Downtime (hr) by Operator and Machine'))
        #multivar_bubble(df,"year","continent", "lifeExp", "pop", aggfunc = "mean",hover_name = "country" , x_label = "this is x label", y_label = "ylabel", color_label = "year", title = "tital")
        
        st.markdown('<hr/>', unsafe_allow_html = True)
        st.plotly_chart(vizHelper.plot_histogram(complete_df_t, 'Hourly Throughput', 'Hourly Throughput','name','box', ['% Eff', 'C/O'], 'Brand wise Histogram of Hourly Throghput', 1100, 550))
        
        st.markdown('<hr/>', unsafe_allow_html = True)
        st.write('Download Complete Dataset')
        AgGrid(complete_df_t.drop(columns=['month_no', 'day_no', 'Month','Day', 'unitPrice','name', 'itemcode', 'C/O']))
        df_xlsx = helper.to_excel(complete_df_t)
        st.download_button(label='📥 Download Dataset',
                            data=df_xlsx ,
                            file_name= 'AutoData.xlsx')
        userManagement.app_logger(username, "Automation Operations")
    else : 
        st.warning(f"Dear {str.title(username)}, Please check you selection again as there seems to be a problem with the data filtering 👆") 

def render_recent_working_day(username):
    st.markdown(hover_size(), unsafe_allow_html=True)
    complete_df_for_lwd = auto.get_complete_auto_data()
    recent_day = complete_df_for_lwd['date'].max()
    complete_df = complete_df_for_lwd[complete_df_for_lwd['date'] == recent_day ]
    recent_day = (pd.to_datetime(recent_day)).strftime("%d %b, %Y")
    complete_df_t, total_output, total_target, total_co, total_percent_co, avg_efficiency, avg_throughput , sorted_months, co_by_month,eff_by_month, throughput_by_month, customer_wise_eff_thr, line_wise_eff_thr, customer_qty, co_by_brand, co_by_line, planned_vs_target = helper.preprocess_auto_lastworking(
        complete_df)
    total_oprs = complete_df_t['opr_code'].nunique()
    total_machines = complete_df_t['machine'].nunique()
    st.header(f"Last Working Day - {recent_day}")
    if len(complete_df) > 0:
        kpi1, kpi2,kpi3, kpi4, kpi5 =  st.columns(5)
        with kpi1:
            st.markdown(f"<h4 style = 'text-align: center; color: red;'>Target Quantity</h4>", unsafe_allow_html= True)
            st.markdown(f"<h3 style = 'text-align: center; color: blue;'>{int(total_target)} Pairs</h3>", unsafe_allow_html= True)

        with kpi2:
            st.markdown(f"<h4 style = 'text-align: center; color: red;'>Output Quantity</h3>", unsafe_allow_html= True)
            st.markdown(f"<h3 style = 'text-align: center; color: blue;'>{int(total_output)} Pairs</h1>", unsafe_allow_html= True)

        with kpi3:
            st.markdown(f"<h4 style = 'text-align: center; color: red;'>Total C/O</h4>", unsafe_allow_html= True)
            st.markdown(f"<h3 style = 'text-align: center; color: blue;'>{int(total_co)}</h3>", unsafe_allow_html= True)
        with kpi4:
            st.markdown(f"<h4 style = 'text-align: center; color: red;'>Avg Efficiency</h4>", unsafe_allow_html= True)
            st.markdown(f"<h3 style = 'text-align: center; color: blue;'>{round(avg_efficiency, 2)} %</h3>", unsafe_allow_html= True)
        with kpi5:
            st.markdown(f"<h4 style = 'text-align: center; color: red;'>Defect Rate</h4>", unsafe_allow_html= True)
            st.markdown(f"<h3 style = 'text-align: center; color: blue;'>{round(complete_df_t['% DR'].mean(), 2)} %</h3>", unsafe_allow_html= True)

        st.markdown('<hr/>', unsafe_allow_html = True)
        kpi1, kpi2,kpi3, kpi4, kpi5 =  st.columns(5)
        with kpi1:
            st.markdown(f"<h4 style = 'text-align: center; color: red;'>Total Working Hour</h4>", unsafe_allow_html= True)
            st.markdown(f"<h3 style = 'text-align: center; color: blue;'>{complete_df_t['total_hours'].sum()} hrs</h3>", unsafe_allow_html= True)

        with kpi2:
            st.markdown(f"<h4 style = 'text-align: center; color: red;'>Machine Downtime</h3>", unsafe_allow_html= True)
            st.markdown(f"<h3 style = 'text-align: center; color: blue;'>{complete_df_t['ms_hours'].sum()} hrs </h1>", unsafe_allow_html= True)

        with kpi3:
            st.markdown(f"<h4 style = 'text-align: center; color: red;'>Man to machine ratio</h4>", unsafe_allow_html= True)
            st.markdown(f"<h3 style = 'text-align: center; color: blue;'>{round(total_oprs/total_machines, 2)}</h3>", unsafe_allow_html= True)
        with kpi4:
            st.markdown(f"<h4 style = 'text-align: center; color: red;'>Total Operators</h4>", unsafe_allow_html= True)
            st.markdown(f"<h3 style = 'text-align: center; color: blue;'>{total_oprs}</h3>", unsafe_allow_html= True)
        with kpi5: 
            st.markdown(f"<h4 style = 'text-align: center; color: red;'>Total Machines</h4>", unsafe_allow_html= True)
            st.markdown(f"<h3 style = 'text-align: center; color: blue;'>{total_machines}</h3>", unsafe_allow_html= True)
        st.markdown('<hr/>', unsafe_allow_html = True)
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Actual", x=planned_vs_target['opr_code'], y=planned_vs_target['Output']))
        fig.add_trace(go.Bar(name="Target", x=planned_vs_target['opr_code'], y=planned_vs_target['Target']))
        fig.update_layout(autosize=False,width=1100,height=500,title='Target Vs Actual')
        st.plotly_chart(fig)
        st.markdown('<hr/>', unsafe_allow_html = True)
        col1, col2 = st.columns(2)
        col1.plotly_chart(vizHelper.line_bar(line_wise_eff_thr, x = line_wise_eff_thr['opr_code'], y1=line_wise_eff_thr['% Eff'], y2=line_wise_eff_thr['Hourly Throughput'],
        legends=['% Eff', 'Hourly Throughput'] ,title='Operator wise % Eff and Hourly Throughput' ))
        col2.plotly_chart(vizHelper.pie_chart(co_by_line, "C/O", 'opr_code', title='Operator wise C/O Ratio'))
        st.markdown('<hr/>', unsafe_allow_html = True)
        st.write('Last Working Day Data')
        AgGrid(complete_df_t.drop(columns=['month_no', 'day_no', 'Month','Day', 'unitPrice','SubCategory', 'itemcode', 'C/O']))
        df_xlsx = helper.to_excel(complete_df_t)
        st.download_button(label='📥 Download Dataset',
                            data=df_xlsx ,
                            file_name= 'AutoData.xlsx')
        userManagement.app_logger(username, "Auto LWD")
    else :
        st.info('The "Last Working Day" data is not available for the selection you made, please scroll up and make the selection again, Thank you!')

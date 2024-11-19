import streamlit as st
from common import helper, vizHelper
from accountsPckg.costing import costing
import adminPckg.userManagement as userManagement
import pandas as pd
import plotly.graph_objects as go
import static.formatHelper as fh
from st_aggrid import AgGrid
from accountsPckg.accounts_helper import preprocess_salaries
from static.formatHelper import hover_size

def get_costing_vars():
    complete_df = costing.get_complete_costing_data()
    date = complete_df['date'].unique().tolist()
    year = complete_df['year'].unique().tolist()
    customer_pos = complete_df.customer_PO.unique().tolist()
    customer_pos.insert(0, 'All POs')   
    customer = complete_df['name'].unique().tolist()
    customer.insert(0, 'All Customers')
    line_number = complete_df['line_number'].unique().tolist()
    line_number.insert(0, 'All Lines')
    mastercode = complete_df['mastercode'].unique().tolist()
    mastercode.insert(0, 'All Master Codes')
    size = complete_df['size'].unique().tolist()
    size.insert(0, 'All Sizes')
    return complete_df, date, year, customer_pos, customer, line_number, mastercode, size

def render_costing_operations(username):
    st.write(fh.format_st_button(), unsafe_allow_html=True)
    st.markdown(hover_size(), unsafe_allow_html=True)
    complete_df, date, year, customer_pos, customer, line_number, mastercode, size = get_costing_vars()

    with st.form(key = "costing_form0"):
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
            st.markdown("**Line Number :**")
            line_selection = st.multiselect('',  line_number, default='All Lines') 
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
    if line_selection ==["All Lines"]:
        line_list = line_number
        line_selection = line_list
    if mastercode_selection ==["All Master Codes"]:
        mastercode_list = mastercode
        mastercode_selection = mastercode_list
    if size_selection == ['All Sizes']:
        size_list = size
        size_selection = size_list

    complete_df_t, avg_throughput ,monthly_throughput_cost_foh,  customer_qty ,customer_selling_price, linewise_cost_foh = helper.preprocess_costing(
        complete_df, start_date, end_date, year, po_selection, customer_selection, line_selection, mastercode_selection, size_selection, lwd=False)
    if isinstance (complete_df_t, pd.DataFrame):
        kpi1, kpi2,kpi3 =  st.columns(3)
        with kpi1:
            avg_foh = round(monthly_throughput_cost_foh['FOH (%)'].mean(), 2)
            st.markdown(f"<h4 style = 'text-align: center; color: red;'>Avg of %FOH</h4>", unsafe_allow_html= True)
            st.markdown(f"<h3 style = 'text-align: center; color: blue;'>{avg_foh} %</h3>", unsafe_allow_html= True)
            with st.expander(" Avg of %FOH Formula"):

                #st.latex(r"$$Avg Eff = \frac{Σ Efficiency}{Σ Working Days}$$")
                st.latex(r'''
                =\left(\frac{Σ Monthly FOH}{Σ Monthly Production Sales Value}\right) * 100
                ''')
        with kpi2:
            st.markdown(f"<h4 style = 'text-align: center; color: red;'>Avg of Per Pair Cost</h3>", unsafe_allow_html= True)
            st.markdown(f"<h3 style = 'text-align: center; color: blue;'>$ {round(monthly_throughput_cost_foh['per_pair_labor_cost'].mean(),2)} </h1>", unsafe_allow_html= True)
            with st.expander("Avg Labour Formula"):
                st.latex(r'''
                =\left(\frac{Σ LaborCost}{Σ OutputQuantity}\right)
                ''')
        with kpi3:
            st.markdown(f"<h4 style = 'text-align: center; color: red;'>Avg Hourly Throughput</h4>", unsafe_allow_html= True)
            st.markdown(f"<h3 style = 'text-align: center; color: blue;'>{int(avg_throughput)}</h3>", unsafe_allow_html= True)
            with st.expander("Hourly Throughput Formula"):
                st.latex(r'''
                =\left(\frac{Σ Output Qty}{Σ Working Hours}\right)
                ''')
        st.markdown('<hr/>', unsafe_allow_html = True)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"<h4 style = 'text-align: center; color: red;'>Total Output</h3>", unsafe_allow_html= True)
            st.markdown(f"<h3 style = 'text-align: center; color: blue;'>{int(monthly_throughput_cost_foh['qty'].sum())}</h1>", unsafe_allow_html= True)
        with col2:
            st.markdown(f"<h4 style = 'text-align: center; color: red;'>Sales Value</h3>", unsafe_allow_html= True)
            st.markdown(f"<h3 style = 'text-align: center; color: blue;'>$ {int(monthly_throughput_cost_foh['selling_price'].sum())}</h1>", unsafe_allow_html= True)
        with col3:
            st.markdown(f"<h4 style = 'text-align: center; color: red;'>Operating Cost</h3>", unsafe_allow_html= True)
            st.markdown(f"<h3 style = 'text-align: center; color: blue;'>$ {int(monthly_throughput_cost_foh['Labor Cost'].sum())}</h1>", unsafe_allow_html= True)

    st.markdown('<hr/>', unsafe_allow_html = True)
    col1, col2 = st.columns(2)
    monthly_throughput_cost_foh = monthly_throughput_cost_foh.dropna(subset=['per_pair_labor_cost'])
    col1.plotly_chart(vizHelper.area_chart(monthly_throughput_cost_foh, 'Month', 'per_pair_labor_cost','Month', 'FOH (%)', "Labor Cost per Pair ($)", unit = '$'))
    col2.plotly_chart(vizHelper.area_chart(monthly_throughput_cost_foh, 'Month', 'Hourly Throughput','Month', 'Hourly Throughput', "Month wise hourly throughput", unit = "/Hr"))
    st.markdown('<hr/>', unsafe_allow_html = True)
    
    col1, col2 = st.columns(2)
    col1.plotly_chart(vizHelper.stacked_area_chart(monthly_throughput_cost_foh, 'Month', 'FOH (%)','Target FOH (%)', ['FOH (%)', 'Target FOH (%)'], "Montly FOH"))
    #col2.plotly_chart(vizHelper.pie_chart(customer_qty, 'Quantity', 'Customer Name', title='Customer wise Production Ratio'))
    
    fig = go.Figure(go.Indicator(
    domain = {'x': [0, 1], 'y': [0, 1]},
    value = avg_foh,
    mode = "gauge+number+delta",
    title = {'text': "FOH (%)"},
    delta = {'reference': monthly_throughput_cost_foh['Target FOH (%)'].mean()},
    gauge = {'axis': {'range': [0, 100]},
            'bar': {'color': "darkblue"},
            'steps' : [
                {'range': [0, 15], 'color': "green"},
                {'range': [15, 40], 'color': "yellow"},
                {'range': [40, 100], 'color': "red"}],
            'threshold' : {'line': {'color': "blue", 'width': 4}, 'thickness': 0.75, 'value': avg_foh}}))
    fig.update_layout(autosize=False,width=600,height=500)
    col2.plotly_chart(fig)
    
    
    st.markdown('<hr/>', unsafe_allow_html = True)
    
    col1, col2 = st.columns(2)
    col1.plotly_chart(vizHelper.pie_chart(customer_qty, 'Quantity', 'Customer Name', title='Customer wise Production Ratio'))
    col2.plotly_chart(vizHelper.pie_chart(customer_selling_price, 'Sales Value', 'Customer Name', title='Customer wise Sales Value'))
    st.markdown('<hr/>', unsafe_allow_html = True)
    
    col1, col2 = st.columns(2)
    col1.plotly_chart(vizHelper.line_bar(linewise_cost_foh, x = linewise_cost_foh['line_number'], y1=linewise_cost_foh['per_pair_labor_cost'], y2=linewise_cost_foh['FOH (%)'],
        legends=['Labor Cost per Pair($)', 'FOH (%)'] ,title='Line wise Labor Cost and FOH (%)' , round_decimal=2))
    linewise_cost_foh_corr = linewise_cost_foh
    linewise_cost_foh_corr["FOH (%)"] = linewise_cost_foh_corr['FOH (%)'].fillna(value=0)
    col2.plotly_chart(vizHelper.bubble_chart(linewise_cost_foh_corr, "Hourly Throughput", "per_pair_labor_cost", "FOH (%)","line_number", "line_number", "Correlation of Throughput and Labor Cost"))
    st.markdown('<hr/>', unsafe_allow_html = True)
    
    st.plotly_chart(vizHelper.plot_histogram(complete_df_t, 'FOH(%)', 'FOH(%)','line_number','box', ['FOH(%)', 'Target FOH (%)', 'Hourly Throughput'], 'Brand wise Histogram of Hourly Throghput', 1100, 550))
    st.markdown('<hr/>', unsafe_allow_html = True)
    
    st.header('Complete Dataset')
    AgGrid(complete_df_t)
    df_xlsx = helper.to_excel(complete_df_t)
    st.download_button(label='📥 Download Dataset',
                        data=df_xlsx ,
                        file_name= 'CostingData.xlsx')

    st.header('Monthly Data')
    AgGrid(monthly_throughput_cost_foh)
    df_xlsx = helper.to_excel(monthly_throughput_cost_foh)
    st.download_button(label='📥 Download Dataset',
                        data=df_xlsx ,
                        file_name= 'MonthwiseCostingData.xlsx')

    st.header('Linewise Data')
    AgGrid(linewise_cost_foh)
    df_xlsx = helper.to_excel(linewise_cost_foh)
    st.download_button(label='📥 Download Dataset',
                        data=df_xlsx ,
                        file_name= 'LinewiseCostingData.xlsx')
    
    userManagement.app_logger(username, "Costing Operations")

def render_recent_working_day(username):
    #complete_df_for_lwd = costing.get_complete_costing_data()
    st.markdown(hover_size(), unsafe_allow_html=True)
    complete_df, date, year, customer_pos, customer, line_number, mastercode, size = get_costing_vars()
    recent_day = complete_df['date'].max().strftime("%d %b, %Y")
    complete_df = complete_df[complete_df['date'] == recent_day ]
    start_date = pd.to_datetime(min(date))
    end_date = pd.to_datetime(max(date))
    complete_df_t, avg_throughput ,monthly_throughput_cost_foh,  customer_qty ,customer_selling_price, linewise_cost_foh = helper.preprocess_costing(
        complete_df, start_date, end_date, year, customer_pos, customer, line_number, mastercode, size, lwd=True)
    
    st.header(f"Last Working Day - {recent_day}")
    if avg_throughput > 0:
        kpi1, kpi2,kpi3 =  st.columns(3)
        with kpi1:
            avg_foh = round(monthly_throughput_cost_foh['FOH (%)'].mean(), 2)
            st.markdown(f"<h4 style = 'text-align: center; color: red;'>Avg of %FOH</h4>", unsafe_allow_html= True)
            st.markdown(f"<h3 style = 'text-align: center; color: blue;'>{avg_foh} %</h3>", unsafe_allow_html= True)
            with st.expander(" Avg of %FOH Formula"):

                #st.latex(r"$$Avg Eff = \frac{Σ Efficiency}{Σ Working Days}$$")
                st.latex(r'''
                =\left(\frac{Σ Monthly FOH}{Σ Monthly Production Sales Value}\right) * 100
                ''')
        with kpi2:
            st.markdown(f"<h4 style = 'text-align: center; color: red;'>Avg of Per Pair Cost</h3>", unsafe_allow_html= True)
            st.markdown(f"<h3 style = 'text-align: center; color: blue;'>$ {round(monthly_throughput_cost_foh['per_pair_labor_cost'].mean(),2)} </h1>", unsafe_allow_html= True)
            with st.expander("Avg Labour Formula"):
                st.latex(r'''
                =\left(\frac{Σ LaborCost}{Σ OutputQuantity}\right)
                ''')
        with kpi3:
            st.markdown(f"<h4 style = 'text-align: center; color: red;'>Avg Hourly Throughput</h4>", unsafe_allow_html= True)
            st.markdown(f"<h3 style = 'text-align: center; color: blue;'>{int(avg_throughput)}</h3>", unsafe_allow_html= True)
            with st.expander("Hourly Throughput Formula"):
                st.latex(r'''
                =\left(\frac{Σ Output Qty}{Σ Working Hours}\right)
                ''')
        st.markdown('<hr/>', unsafe_allow_html = True)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"<h4 style = 'text-align: center; color: red;'>Total Output</h3>", unsafe_allow_html= True)
            st.markdown(f"<h3 style = 'text-align: center; color: blue;'>{int(monthly_throughput_cost_foh['qty'].sum())}</h1>", unsafe_allow_html= True)
        with col2:
            st.markdown(f"<h4 style = 'text-align: center; color: red;'>Sales Value</h3>", unsafe_allow_html= True)
            st.markdown(f"<h3 style = 'text-align: center; color: blue;'>$ {int(monthly_throughput_cost_foh['selling_price'].sum())}</h1>", unsafe_allow_html= True)
        with col3:
            st.markdown(f"<h4 style = 'text-align: center; color: red;'>Operating Cost</h3>", unsafe_allow_html= True)
            st.markdown(f"<h3 style = 'text-align: center; color: blue;'>$ {int(monthly_throughput_cost_foh['Labor Cost'].sum())}</h1>", unsafe_allow_html= True)
        st.markdown('<hr/>', unsafe_allow_html = True)

        col1, col2 = st.columns(2)
        fig = go.Figure(go.Indicator(
        domain = {'x': [0, 1], 'y': [0, 1]},
        value = avg_foh,
        mode = "gauge+number+delta",
        title = {'text': "FOH (%)"},
        delta = {'reference': monthly_throughput_cost_foh['Target FOH (%)'].mean()},
        gauge = {'axis': {'range': [0, 100]},
                'bar': {'color': "darkblue"},
                'steps' : [
                    {'range': [0, 15], 'color': "green"},
                    {'range': [15, 40], 'color': "yellow"},
                    {'range': [40, 100], 'color': "red"}],
                'threshold' : {'line': {'color': "blue", 'width': 4}, 'thickness': 0.75, 'value': avg_foh}}))
        fig.update_layout(autosize=False,width=600,height=500)
        col1.plotly_chart(fig)
        col2.plotly_chart(vizHelper.line_bar(linewise_cost_foh, x = linewise_cost_foh['line_number'], y1=linewise_cost_foh['qty'], y2=linewise_cost_foh['Hourly Throughput'],
        legends=['Output Qty', 'Hourly Throughput'] ,title='Line wise Labor Cost and Hourly Throughput' ))
        st.markdown('<hr/>', unsafe_allow_html = True)
        
        col1, col2 = st.columns(2)
        col1.plotly_chart(vizHelper.pie_chart(customer_qty, 'Quantity', 'Customer Name', title='Customer wise Production Ratio'))
        col2.plotly_chart(vizHelper.pie_chart(customer_selling_price, 'Sales Value', 'Customer Name', title='Customer wise Sales Value'))
        st.markdown('<hr/>', unsafe_allow_html = True)

        col1, col2 = st.columns(2)
        linewise_cost_foh = linewise_cost_foh.dropna()
        col1.plotly_chart(vizHelper.line_bar(linewise_cost_foh, x = linewise_cost_foh['line_number'], y1=linewise_cost_foh['per_pair_labor_cost'], y2=linewise_cost_foh['FOH (%)'],
            legends=['Labor Cost per Pair($)', 'FOH (%)'] ,title='Line wise Labor Cost and FOH (%)' ))
        linewise_cost_foh_corr = linewise_cost_foh
        linewise_cost_foh_corr["FOH (%)"] = linewise_cost_foh_corr['FOH (%)'].fillna(value=0)
        col2.plotly_chart(vizHelper.bubble_chart(linewise_cost_foh_corr, "Hourly Throughput", "per_pair_labor_cost", "qty" ,"line_number", "line_number", "Correlation of Throughput and Labor Cost"))
        st.markdown('<hr/>', unsafe_allow_html = True)
        
        st.header('Dataset')
        AgGrid(complete_df_t)
        df_xlsx = helper.to_excel(complete_df_t)
        st.download_button(label='📥 Download Dataset',
                        data=df_xlsx ,
                        file_name= 'CostingData_LastWorkingDay.xlsx')
        userManagement.app_logger(username, "Costing LWD")
    else :
        st.error('The "Last Working Day" data is not available for the selection you made, please scroll up and make the selection again, Thank you!')


def render_costing_form(username):
    complete_df = costing.get_complete_costing_data()
    month_list = complete_df['Month'].unique().tolist()
    year_list = complete_df['year'].unique().tolist()
    
    with st.form(key="pro_lab_cost_form"):
        form_title_pro_lab_cost = 'Production Labor Cost Form'
        st.header(form_title_pro_lab_cost)
        col1, col2 = st.columns(2)
        with col1:
            month_selection = st.selectbox('Month',options = month_list)
        with col2:
            year_selection = st.selectbox('Year',options = year_list)
        month_year = (str(month_selection)+str(year_selection))
        uploaded_file = st.file_uploader('📤 Upload an Excel File')
        #st.write(fh.format_st_button(), unsafe_allow_html=True)
        required_format  = '[Check the Required Format](https://bhglovesltd-my.sharepoint.com/:x:/g/personal/hasnain_bhgloves_com/EW6n5B7CjQ1FgVsKrSeRV9oBDiPQYHpg2ECk-bWJKnGOVA?e=SOc7GZ)'
        st.markdown(required_format, unsafe_allow_html=True)
        submit_lab_cost = st.form_submit_button(label = 'Submit Form')

    if submit_lab_cost:
        if uploaded_file is not None:
            try:
                df = pd.read_excel(uploaded_file, engine="openpyxl")
            except:
                st.warning('Make sure to upload an excel file. The preferred extension for the file is "xlsx"')
            try:
                cursor_sql_wh , conn_sql_wh = helper.connect_sql_olap()
                for index, row in df.iterrows():
                    line_number, labor_cost = row[0], row[1]
                    sql = ('INSERT INTO PRO_LAB_COST(line_number, labor_cost, month_year) values(%s, %s, %s)')
                    cursor_sql_wh.execute(sql, [line_number, labor_cost, month_year])
                conn_sql_wh.commit()
                conn_sql_wh.close()
                st.success(f"{form_title_pro_lab_cost} has been submitted successfully")
                userManagement.app_logger(username, "New Entry for Labor Cost")
            except:
                st.error("The Data Already Exits. Please Contact Admin in case the problem persists ")
                
    with st.form(key = 'foh_form'):
        foh_form_title = "FOH Form"
        st.header(foh_form_title)
        col1, col2 = st.columns(2)
        with col1:
            month_selection = st.selectbox('Month',options = month_list)
        with col2:
            year_selection = st.selectbox('Year',options = year_list)
        month_year = (str(month_selection)+str(year_selection))
        col1, col2 = st.columns(2)
        with col1:
            FOH_VALUE = st.number_input("FOH ($)")
        with col2:
            TARGET_FOH = st.number_input("Target %FOH")
            if TARGET_FOH > 1 :
                TARGET_FOH = TARGET_FOH/100
        submit_foh = st.form_submit_button(label = 'Submit Form')

        if submit_foh:
            try:
                cursor_sql_wh , conn_sql_wh = helper.connect_sql_olap()
                sql = ('INSERT INTO MONTHLY_FOH(month_year, FOH_VALUE, TARGET_FOH ) values(%s, %s, %s)')
                cursor_sql_wh.execute(sql, [month_year, FOH_VALUE, TARGET_FOH])
                conn_sql_wh.commit()
                conn_sql_wh.close()
                st.success(f"{foh_form_title} has been submitted successfully! ")
                userManagement.app_logger(username, "New Entry for Monthly FOH")
            except:
                st.error("The Data Already Exits. Please Contact Admin in case the problem persists ")

    with st.form(key='edit_foh_form'):
        edit_foh_form_title = "Edit Monthly FOH"
        st.header(edit_foh_form_title)

        foh_df = helper.get_foh_data()
        month_year = foh_df['month_year'].unique().tolist()
        month = set([element[0:3] for element in month_year])
        year = set([element[3:] for element in month_year])
        col1, col2 = st.columns(2)
        with col1:
            month_selection = st.selectbox('Month',options = month)
        with col2:
            year_selection = st.selectbox('Year',options = year)
        month_year = str(month_selection)+str(year_selection)
        col1, col2 = st.columns(2)
        with col1:
            FOH_VALUE = st.number_input("FOH ($)")
        with col2:
            TARGET_FOH = st.number_input("Target %FOH")
            if TARGET_FOH > 1 :
                TARGET_FOH = TARGET_FOH/100
        submit_foh_edit = st.form_submit_button(label = '📝Edit Data!')
        
        if submit_foh_edit:
            try:
                cursor_sql_wh , conn_sql_wh = helper.connect_sql_olap()
                sql = ('''DELETE FROM MONTHLY_FOH WHERE MONTH_YEAR = %s ''')
                cursor_sql_wh.execute(sql, [month_year])
                conn_sql_wh.commit()
                
                sql = ('INSERT INTO MONTHLY_FOH(month_year, FOH_VALUE, TARGET_FOH ) values(%s, %s, %s)')
                cursor_sql_wh.execute(sql, [month_year, FOH_VALUE, TARGET_FOH])
                conn_sql_wh.commit()
                conn_sql_wh.close()
                st.success(f'The data has been updated for "{month_year}" 🎉')
                userManagement.app_logger(username, "Edit Monthly FOH")
            except:
                st.error("Sorry, Could not update the data. Please Contact Admin in case the problem persists ")

    with st.form(key='edit_lab_cost_form'):
        edit_foh_form_title = "Edit Labor Cost"
        st.header(edit_foh_form_title)

        lab_cost_df = helper.get_pro_lab_cost()
        month_year = lab_cost_df['month_year'].unique().tolist()
        month = set([element[0:3] for element in month_year])
        year = set([element[3:] for element in month_year])
        col1, col2 = st.columns(2)
        with col1:
            month_selection = st.selectbox('Month',options = month)
        with col2:
            year_selection = st.selectbox('Year',options = year)
        month_year = str(month_selection)+str(year_selection)

        uploaded_file = st.file_uploader('📤 Upload the data to be edited')
        #st.write(fh.format_st_button(), unsafe_allow_html=True)
        required_format  = '[Check the Required Format](https://bhglovesltd-my.sharepoint.com/:x:/g/personal/hasnain_bhgloves_com/EW6n5B7CjQ1FgVsKrSeRV9oBDiPQYHpg2ECk-bWJKnGOVA?e=SOc7GZ)'
        st.markdown(required_format, unsafe_allow_html=True)

        submit_lab_cost_edit = st.form_submit_button(label = '📝Edit Data!')
        
        if submit_lab_cost_edit:
            if uploaded_file is not None:
                try:
                    df = pd.read_excel(uploaded_file, engine='openpyxl')
                except: 
                    st.warning('Make sure to upload an excel file. The preferred extension for the file is "xlsx"')
                try:
                    cursor_sql_wh , conn_sql_wh = helper.connect_sql_olap()
                    sql = ('''DELETE FROM PRO_LAB_COST
                            WHERE MONTH_YEAR = %s ''')
                    cursor_sql_wh.execute(sql, [month_year])
                    conn_sql_wh.commit()
                    for index, row in df.iterrows():
                        line_number, cost = row[0], row[1]
                        sql = ('INSERT INTO PRO_LAB_COST(line_number, labor_cost, month_year) values(%s, %s, %s)')
                        cursor_sql_wh.execute(sql, [line_number, cost, month_year])
                    conn_sql_wh.commit()
                    st.success(f'The data has been updated for "{month_year}" 🎉')
                    userManagement.app_logger(username, "Edit Labor Cost")
                except :
                    st.error("Sorry, Could not update the data. Please Contact Admin in case the problem persists ")
            else:
                st.error("Kindly upload the data file")


    st.header('FOH in Database')
    AgGrid(foh_df)
    df_xlsx = helper.to_excel(foh_df)
    st.download_button(label='📥 Download Dataset',
                        data=df_xlsx ,
                        file_name= 'FOHfromDatabase.xlsx')

    st.header('Labor Cost in Database')
    AgGrid(lab_cost_df)
    df_xlsx = helper.to_excel(lab_cost_df)
    st.download_button(label='📥 Download Dataset',
                        data=df_xlsx ,
                        file_name= 'LaborCostFromDatabase.xlsx')

def render_salary_form(username):
    engine = helper.get_db_engine(helper.DB_CENT_USR, helper.DB_CENT_PASS , helper.DB_CENT_HOST, helper.DB_CENT_NAME)
    month_list = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    year_list = ['2020', '2021', '2022', '2023', '2024']
    with st.form(key='salary-form'):
        st.header('Add Monthly Salary')
        col1, col2 = st.columns(2)
        with col1:
            month = st.selectbox('Select a Month', month_list)
        with col2:
            year  = st.selectbox('Select a Year', year_list)
        st.subheader('📤 Please Upload an Excel file')
        uploaded_data = st.file_uploader('')
        required_format  = '[Check the Required Format](https://bhglovesltd-my.sharepoint.com/:x:/g/personal/hasnain_bhgloves_com/EcQKA2aBOuJCq1e4nRHnvYIBj21oiF37zlEG9KBzsq5kig?e=bFwtmp)'
        st.markdown(required_format, unsafe_allow_html=True)
        submit_salary_form = st.form_submit_button(label = '✔ Submit Form')
        
        if submit_salary_form:
            if uploaded_data is not None:
                try:
                    try:
                        salaries = preprocess_salaries(uploaded_data, month, year)
                        st.success(f"Great work {str.title(username)}! Data has been validated Successfully 🎉")
                        salaries.to_sql(name='tblsalaries', con=engine, index=False, if_exists='append')
                        st.success(f"Well done {str.title(username)}! Data has been Upload Successfully 🎊")
                        userManagement.app_logger(username, "Add Monthly Salaries")
                    except:
                        st.error(f"Oh {str.title(username)}, data could not be uploaded in the database because same data may already exist in the database or the provided file format is not correct. Please contact admin in case the problem persists. We are sorry 😌")
                except:
                    st.error(f"Dear {str.title(username)}, file could not be uploaded properly. Please contact admin in case the problem persists. We are sorry 😌")
    
    with st.form(key='edit_salaries_form'):
        st.header("Edit Monthly Salaries")

        salaries_df = pd.read_sql("tblsalaries", engine)
        month_year = salaries_df['month_year'].unique().tolist()
        month = set([element[0:3] for element in month_year])
        year = set([element[3:] for element in month_year])
        col1, col2 = st.columns(2)
        with col1:
            month = st.selectbox('Month',options = month)
        with col2:
            year = st.selectbox('Year',options = year)
        month_year = str(month)+str(year)
        
        st.subheader('📤 Please Upload an Excel file')
        uploaded_data = st.file_uploader('')
        required_format  = '[Check the Required Format](https://bhglovesltd-my.sharepoint.com/:x:/g/personal/hasnain_bhgloves_com/EcQKA2aBOuJCq1e4nRHnvYIBj21oiF37zlEG9KBzsq5kig?e=bFwtmp)'
        st.markdown(required_format, unsafe_allow_html=True)

        submit_salaries_edit = st.form_submit_button(label = '📝Edit Data')
        
        if submit_salaries_edit:
            try:
                cursor_sql_wh , conn_sql_wh = helper.connect_sql_olap()
                query = ('''DELETE FROM bhvn_olap.tblsalaries WHERE month_year = %s''')
                cursor_sql_wh.execute(query, [month_year])
                conn_sql_wh.commit()
                salaries = preprocess_salaries(uploaded_data, month, year)
                salaries.to_sql(name='tblsalaries', con=engine, index=False, if_exists='append')
                conn_sql_wh.commit()
                conn_sql_wh.close()
                st.success(f'The data has been updated for "{month_year}" 🎉')
                userManagement.app_logger(username, "Edit Monthly Salaries")
            except:
                st.error("Sorry, Could not update the data. Please Contact Admin in case the problem persists ")
    
    st.header('Salaries Data in Database')
    salaries_db = pd.read_sql("tblsalaries", engine)
    AgGrid(salaries_db)
    df_xlsx = helper.to_excel(salaries_db)
    st.download_button(label='📥 Download Dataset',
                        data=df_xlsx ,
                        file_name= 'SalariesData.xlsx')
    userManagement.app_logger(username, "Salary Form")            
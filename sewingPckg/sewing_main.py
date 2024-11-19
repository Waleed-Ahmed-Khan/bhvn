import streamlit as st
from common import helper, vizHelper
import sewingPckg.sewing as sewing, adminPckg.userManagement as userManagement
import pandas as pd
import plotly.graph_objects as go
import static.formatHelper as fh
from st_aggrid import AgGrid
from sewingPckg.sewing_helper import preprocess_performance_form, preprocess_performance_data, get_performance_variables
from PIL import Image
import os
from static.formatHelper import hover_size
from common import sqlDBManagement
import appConfig as CONFIG


def render_sewing_operations(username):
    st.markdown(hover_size(), unsafe_allow_html=True)
    st.write(fh.format_st_button(), unsafe_allow_html=True)
    with st.spinner("Sewing Dashboard is Getting Ready ... 🧤"):
        complete_df = sewing.get_complete_sewing_data()
    date = complete_df['date'].unique().tolist()
    year = complete_df['year'].unique().tolist()
    year = year[::-1] # reverse the list for ['current_year', 2021]
    customer_pos = complete_df.customer_PO.unique().tolist()
    customer_pos.insert(0, 'All POs')   
    customer = complete_df['SubCategory'].unique().tolist()
    customer.insert(0, 'All Customers')
    line_number = complete_df['line_number'].unique().tolist()
    line_number.insert(0, 'All Lines')
    mastercode = complete_df['mastercode'].unique().tolist()
    mastercode.insert(0, 'All Master Codes')
    size = complete_df['size'].unique().tolist()
    size.insert(0, 'All Sizes')

    with st.form(key = "sewing_form"):
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

    complete_df_t, total_output, total_target, total_co, total_percent_co, avg_efficiency, avg_throughput , sorted_months, co_by_month,eff_by_month, throughput_by_month, customer_wise_eff_thr, line_wise_eff_thr, customer_qty, co_by_brand, co_by_line = helper.preprocess_sewing(
        complete_df, start_date, end_date, year, po_selection, customer_selection, line_selection, mastercode_selection, size_selection)
    
    if isinstance (complete_df_t, pd.DataFrame):
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
    col1, col2 = st.columns(2, gap = 'small')
    col1.plotly_chart(vizHelper.area_chart(eff_by_month, 'Month', '% Eff','Month', '% Eff', "Month wise Efficiency", unit = "%"))
    col2.plotly_chart(vizHelper.area_chart(throughput_by_month, 'Month', 'Hourly Throughput','Month', 'Hourly Throughput', "Month wise hourly throughput", unit = "/Hr"))
    st.markdown('<hr/>', unsafe_allow_html = True)
    col1, col2 = st.columns(2)
    col1.plotly_chart(vizHelper.area_chart(co_by_month, 'Month', 'percent_co','Month', '% C/O', "Month wise Percentage C/O", unit = "%"))
    col2.plotly_chart(vizHelper.pie_chart(customer_qty, 'Quantity', 'Customer Name', title='Customer wise Production Ratio'))
    st.markdown('<hr/>', unsafe_allow_html = True)
    col1, col2 = st.columns(2)
    col1.plotly_chart(vizHelper.line_bar(line_wise_eff_thr, x = line_wise_eff_thr['line_number'], y1=line_wise_eff_thr['% Eff'], y2=line_wise_eff_thr['Hourly Throughput'],
        legends=['% Eff', 'Hourly Throughput'] ,title='Line wise % Eff and Hourly Throughput' ))
    col2.plotly_chart(vizHelper.line_bar(customer_wise_eff_thr, x = customer_wise_eff_thr['SubCategory'], y1=customer_wise_eff_thr['% Eff'], y2=customer_wise_eff_thr['Hourly Throughput'],
    legends=['% Eff', 'Hourly Throughput'] ,title='Customer wise % Eff and Hourly Throughput' ))
    st.markdown('<hr/>', unsafe_allow_html = True)
    col1, col2 = st.columns(2)
    col1.plotly_chart(vizHelper.pie_chart(co_by_brand, 'C/O','SubCategory', title='Brand wise C/O Ratio' ))
    col2.plotly_chart(vizHelper.pie_chart(co_by_line, "C/O", 'line_number', title='Line wise C/O Ratio'))

    st.markdown('<hr/>', unsafe_allow_html = True)
    st.plotly_chart(vizHelper.plot_histogram(complete_df_t, 'Hourly Throughput', 'Hourly Throughput','name','box', ['% Eff', 'C/O'], 'Brand wise Histogram of Hourly Throghput', 1100, 550))
    
    st.markdown('<hr/>', unsafe_allow_html = True)
    st.write('Download Complete Dataset')
    AgGrid(complete_df_t.drop(columns=['month_no', 'day_no', 'Month','Day', 'unitPrice','name', 'itemcode', 'C/O']))
    # st.download_button(
    # '📥 Download Dataset',complete_df_t.to_csv( index = False ).encode('utf-8'),
    # "SewingData.csv","text/csv",key='download-csv'
    # )
    df_xlsx = helper.to_excel(complete_df_t)
    st.download_button(label='📥 Download Dataset',
                                data=df_xlsx ,
                                file_name= 'SewingData.xlsx')

    userManagement.app_logger(username, "Sewing Operations")

def render_recent_working_day(username):
    st.markdown(hover_size(), unsafe_allow_html=True)
    complete_df_for_lwd = sewing.get_complete_sewing_data()
    recent_day = complete_df_for_lwd['date'].max().strftime("%d %b, %Y")
    complete_df = complete_df_for_lwd[complete_df_for_lwd['date'] == recent_day ]
    complete_df_t, total_output, total_target, total_co, total_percent_co, avg_efficiency, avg_throughput , sorted_months, co_by_month,eff_by_month, throughput_by_month, customer_wise_eff_thr, line_wise_eff_thr, customer_qty, co_by_brand, co_by_line, planned_vs_target = helper.preprocess_sewing_lastworking(
        complete_df)
    st.header(f"Last Working Day - {recent_day}")
    if total_target > 0:
        try:
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
            fig.add_trace(go.Bar(name="Actual", x=planned_vs_target['line_number'], y=planned_vs_target['Output']))
            fig.add_trace(go.Bar(name="Target", x=planned_vs_target['line_number'], y=planned_vs_target['Target']))
            fig.update_layout(autosize=False,width=1100,height=500,title='Target Vs Actual')
            st.plotly_chart(fig)
            st.markdown('<hr/>', unsafe_allow_html = True)
            col1, col2 = st.columns(2)
            col1.plotly_chart(vizHelper.line_bar(line_wise_eff_thr, x = line_wise_eff_thr['line_number'], y1=line_wise_eff_thr['% Eff'], y2=line_wise_eff_thr['Hourly Throughput'],
            legends=['% Eff', 'Hourly Throughput'] ,title='Line wise % Eff and Hourly Throughput' ))
            col2.plotly_chart(vizHelper.pie_chart(co_by_line, "C/O", 'line_number', title='Line wise C/O Ratio'))
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
                                        file_name= 'SewingData.xlsx')
            userManagement.app_logger(username, "Sewing LWD")
        except Exception as e:
            raise e
    else :
        st.write('The "Last Working Day" data is not available for the selection you made, please scroll up and make the selection again, Thank you!')


def render_sewing_form(username):
    #engine = helper.get_db_engine(helper.SQL_DWH_PASS)
    if CONFIG.BHVN_CENT_DB_SESSION not in st.session_state:
        st.session_state[CONFIG.BHVN_CENT_DB_SESSION] = sqlDBManagement(host = helper.DB_CENT_HOST, username = helper.DB_CENT_USR,
                            password = helper.DB_CENT_PASS, database = helper.DB_CENT_NAME)
    # if "bhvnMysql" not in st.session_state:
    #     st.session_state["bhvnMysql"] = helper.mysqlDBManagement(host = helper.OLAP_HOST, username = helper.OLAP_USER_NAME,
    #                         password = helper.SQL_DWH_PASS, database = helper.OLAP_DB_NAME)
    engine = st.session_state[CONFIG.BHVN_CENT_DB_SESSION].engine
    month_list = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    year_list = ['2020', '2021', '2022', '2023', '2024']
    with st.form(key='performance-form'):
        st.header('Add Monthly Worker Performance')
        col1, col2 = st.columns(2)
        with col1:
            month = st.selectbox('Select a Month', month_list)
        with col2:
            year  = st.selectbox('Select a Year', year_list)
        st.subheader('📤 Please Upload an Excel file')
        uploaded_data = st.file_uploader('')
        required_format  = '[Check the Required Format](https://bhglovesltd-my.sharepoint.com/:x:/g/personal/hasnain_bhgloves_com/EbCXBd_YGtJHhyAI60GmxuQBXhjnV6s2gkjqbv6e_pDWFQ?e=HGzP1Z)'
        st.markdown(required_format, unsafe_allow_html=True)
        submit_salary_form = st.form_submit_button(label = '✔ Submit Form')
        
        if submit_salary_form:
            if uploaded_data is not None:
                try:
                    try:
                        performance = preprocess_performance_form(uploaded_data, month, year)
                        st.success(f"Great work {str.title(username)}! Data has been validated Successfully 🎉")
                        performance.to_sql(name='tblwrkperformance', con=engine, index=False, if_exists='append')
                        st.success(f"Well done {str.title(username)}! Data has been Upload Successfully 🎊")
                        userManagement.app_logger(username, "Add Monthly Worker Performance")
                    except:
                        st.error(f"Oh {str.title(username)}, data could not be uploaded in the database because same data may already exist in the database or the provided file format is not correct. Please contact admin in case the problem persists. We are sorry 😌")
                except:
                    st.error(f"Dear {str.title(username)}, file could not be uploaded properly. Please contact admin in case the problem persists. We are sorry 😌")
    
    with st.form(key='edit_salaries_form'):
        st.header("Edit Monthly Performance")
        salaries_df = st.session_state[CONFIG.BHVN_CENT_DB_SESSION].getDataFramebyQuery("SELECT * FROM tblwrkperformance;")
        #salaries_df = pd.read_sql("tblwrkperformance", engine)
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
        required_format  = '[Check the Required Format](https://bhglovesltd-my.sharepoint.com/:x:/g/personal/hasnain_bhgloves_com/EbCXBd_YGtJHhyAI60GmxuQBXhjnV6s2gkjqbv6e_pDWFQ?e=HGzP1Z)'
        st.markdown(required_format, unsafe_allow_html=True)

        submit_salaries_edit = st.form_submit_button(label = '📝Edit Data')
        
        if submit_salaries_edit:
            try:
                cursor_sql_wh , conn_sql_wh = helper.connect_sql_olap()
                query = ('''DELETE FROM bhvn_olap.tblwrkperformance WHERE month_year = %s''')
                cursor_sql_wh.execute(query, [month_year])
                conn_sql_wh.commit()
                salaries = preprocess_performance_form(uploaded_data, month, year)
                salaries.to_sql(name='tblwrkperformance', con=engine, index=False, if_exists='append')
                conn_sql_wh.commit()
                conn_sql_wh.close()
                st.success(f'The data has been updated for "{month_year}" 🎉')
                userManagement.app_logger(username, "Edit Monthly Performance")
            except:
                st.error("Sorry, Could not update the data. Please Contact Admin in case the problem persists ")
    
    st.header('Worker performance Data in Database')
    performance_db = pd.read_sql("tblwrkperformance", engine)
    AgGrid(performance_db)
    df_xlsx = helper.to_excel(performance_db)
    st.download_button(label='📥 Download Dataset',
                        data=df_xlsx ,
                        file_name= 'WorkerPerformanceData.xlsx')
    userManagement.app_logger(username, "Downloaded Worker Performance Data") 

def render_performance_report(username):
    st.markdown(hover_size(), unsafe_allow_html=True)
    performance, emp_code_list, line_list, date = get_performance_variables()
    with st.form(key = "sewing_form"):
        col1, col2, col3, col4 =  st.columns(4)
        with col1:
            st.markdown("**Employee Code :**")
            emp_code_selection = st.selectbox('',  emp_code_list)
        with col2:
            st.markdown("**Start Date :**")
            start_date = st.date_input('', pd.to_datetime(min(date)))
        with col3:
            st.markdown("**End Date :**")
            end_date = st.date_input('', pd.to_datetime(max(date)))
            #date_selection = st.slider('',min_value=min(date), max_value=max(date), value=(min(date),max(date))) 
        with col4:
            st.markdown("**Line Number :**")
            line_selection = st.multiselect('',  line_list, default='All Lines')

        st.markdown('<hr/>', unsafe_allow_html = True)
        st.form_submit_button(label = '📈 Build Dashboard')
        
    if line_selection ==["All Lines"]:
        line_selection = line_list



    performance, operation_wise, machine_wise, line_wise = preprocess_performance_data(performance,emp_code_selection, line_selection, start_date, end_date)
    if len(performance)>0 :
        col1, col2,col3 =  st.columns(3)
        with col1:
            st.markdown(f"<h4 style = 'text-align: center; color: red;'>Worker Name</h4>", unsafe_allow_html= True)
            st.markdown(f"<h3 style = 'text-align: center; color: blue;'>{str(performance['Name'].unique()[0])}</h3>", unsafe_allow_html= True)

        with col2:
            st.markdown(f"<h4 style = 'text-align: center; color: red;'>Joining Date</h3>", unsafe_allow_html= True)
            st.markdown(f"<h3 style = 'text-align: center; color: blue;'>{(performance['JoiningDate'].unique()[0])}</h1>", unsafe_allow_html= True)

        with col3:
            st.markdown(f"<h4 style = 'text-align: center; color: red;'>Designation</h4>", unsafe_allow_html= True)
            st.markdown(f"<h3 style = 'text-align: center; color: blue;'>{(performance['Designation'].unique()[0])}</h3>", unsafe_allow_html= True)
        st.markdown('<hr/>', unsafe_allow_html = True)
        col1, col2,col3 =  st.columns(3)
        with col1:
            st.markdown(f"<h4 style = 'text-align: center; color: red;'>Avg Efficiency</h4>", unsafe_allow_html= True)
            st.markdown(f"<h3 style = 'text-align: center; color: blue;'>{round(performance['Efficiency'].mean(), 2)}%</h3>", unsafe_allow_html= True)

        with col2:
            st.markdown(f"<h4 style = 'text-align: center; color: red;'>Avg Hourly Throughput</h3>", unsafe_allow_html= True)
            st.markdown(f"<h3 style = 'text-align: center; color: blue;'>{int(performance['HourlyThroughput'].mean())}/Hr</h1>", unsafe_allow_html= True)

        with col3:
            st.markdown(f"<h4 style = 'text-align: center; color: red;'>Total Productivity Bonus</h4>", unsafe_allow_html= True)
            st.markdown(f"<h3 style = 'text-align: center; color: blue;'>{round(performance['pbVND'].sum(), 0)}₫</h3>", unsafe_allow_html= True)
        st.markdown('<hr/>', unsafe_allow_html = True)
        st.markdown('<br><br/>', unsafe_allow_html = True)
        col1, col2 = st.columns(2)
        try:
            worker_images_dir = 'static/worker_images'
            worker_code = str(performance['EmployeeCode'].unique().tolist()[0]) + ".jpg"
            full_path_to_image = os.path.join(os.getcwd(),worker_images_dir, worker_code)
            image = Image.open(full_path_to_image)
            new_image = image.resize((420, 480))
            st.image(new_image, caption='Employee Profile Picture')
        except:
            col1.markdown('<br><br/>', unsafe_allow_html = True)
            col1.markdown('<br><br/>', unsafe_allow_html = True)
            col1.markdown('<br><br/>', unsafe_allow_html = True)
            col1.error("Yikes, Employee Profile Picture is NOT Available 🤦‍♂️")
        col2.plotly_chart(vizHelper.stack_or_group_chart(operation_wise,cat_var='Operation', num_var = ['Efficiency', 'HourlyThroughput', 'TimeLoss', 'pbVND'], title="Operation Wise Worker Performance" ))
        st.markdown('<hr/>', unsafe_allow_html = True)
        col1, col2 = st.columns(2)
        col1.plotly_chart(vizHelper.stack_or_group_chart(machine_wise,cat_var='MachineType', num_var = ['Efficiency', 'HourlyThroughput', 'TimeLoss', 'pbVND'], title="Machine Wise Worker Performance"))
        col2.plotly_chart(vizHelper.stack_or_group_chart(line_wise,cat_var='Line', num_var = ['Efficiency', 'HourlyThroughput', 'TimeLoss', 'pbVND'], title = "Line wise Worker Performance" ))
        userManagement.app_logger(username, "Sewing Worker Performance Report") 
    else:
        st.error(f"Dear {str.title(username)}, there is no data available for your selection, we are sorry 😌 Please change the filter values 👆")
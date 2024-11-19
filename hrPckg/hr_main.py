
import streamlit as st
from common import helper, vizHelper
import adminPckg.userManagement as userManagement
import pandas as pd
import static.formatHelper as fh
from st_aggrid import AgGrid
from hrPckg import hr_helper
from static.formatHelper import hover_size
from vizpool.interactive import EDA
from PIL import Image
import os

@st.cache(suppress_st_warning=True, allow_output_mutation=True, show_spinner=False, ttl=1000)
def get_hr_vars():
    with st.spinner("Please stay with us while we get things ready for you... ⏳"):
        MainEmpStatus, EmpAtt, MainEmpHistory = hr_helper.get_hr_data()
        EmpAtt['Year'] = EmpAtt['AttDate'].dt.year
        date = EmpAtt['AttDate'].unique().tolist()
        emp_id = EmpAtt['EmployeeID'].unique().tolist()
        emp_id.insert(0, 'All Employees')   
        department = MainEmpStatus['Department'].unique().tolist()
        department.insert(0, 'All Departments')
        designation = MainEmpStatus['Position'].unique().tolist()
        designation.insert(0, 'All Designations')
        marital_status = MainEmpStatus['MaritalStatus'].unique().tolist()
        marital_status.insert(0, 'All Status')
        gender = MainEmpStatus['Gender'].unique().tolist()
        gender.insert(0, 'All Genders')
        year = EmpAtt['Year'].unique().tolist()
        return MainEmpStatus, EmpAtt, MainEmpHistory, emp_id, date, department, designation, marital_status, gender, year

@st.cache(suppress_st_warning=True, show_spinner=False, ttl=1000)
def get_medical_vars():
    with st.spinner("Please stay with us while we generate Employee Health Analysis for you... 🛃"):
        MainMedical = hr_helper.get_medical_data()
        MainMedical = MainMedical.astype({'Department': str})
        MainMedical['EmployeeID'] = MainMedical['EmployeeID'].replace(to_replace = ['OFICE', 'oFFICE'], value = ['OFFICE', 'OFFICE'])
        emp_id = MainMedical['EmployeeID'].unique().tolist()
        emp_id.insert(0, 'All Employees')   
        department = MainMedical['Department'].unique().tolist()
        department.insert(0, 'All Departments')
        month = MainMedical['Month'].unique().tolist()
        month.insert(0, 'All Months')
        year = MainMedical['Year'].unique().tolist()
        return MainMedical, emp_id, department, month, year
class RenderHR:
    def __init__(self):
        pass 
    def render_hr_operations(self, username):
        st.write(fh.format_st_button(), unsafe_allow_html=True)
        st.markdown(hover_size(), unsafe_allow_html=True)
        MainEmpStatus, EmpAtt, MainEmpHistory, emp_id, date, department, designation, marital_status, gender, year = get_hr_vars()

        with st.form(key = "hr_form0"):
            col1, col2, col3 =  st.columns(3)
            with col1:
                st.markdown("**Start Date :**")
                start_date = st.date_input('', pd.to_datetime(min(date)))
            with col2:
                st.markdown("**End Date :**")
                end_date = st.date_input('', pd.to_datetime(max(date)))
            with col3:
                st.markdown("**Year :**")
                year_selection = st.selectbox('',  year)
            st.markdown('<hr/>', unsafe_allow_html = True)
            st.form_submit_button(label = '📈 Build Dashboard')
            

        (main_df, MainEmpStatus, MainEmpHistory, monthly_absenteeism, absenteeism_by_age, absenteeism_by_position,
                absenteeism_by_department, absenteeism_by_gender,absenteeism_by_marital_status, absenteeism_by_day_of_week, absenteeism_combined)= hr_helper.hr_data_prep(MainEmpStatus, EmpAtt, MainEmpHistory, start_date, end_date, emp_id, 
                                                                                                                    department, designation, marital_status, gender, year_selection)
        self.MainEmpStatus = MainEmpStatus
        if isinstance (main_df, pd.DataFrame) and len(main_df)>0:
            try:
                kpi1, kpi2,kpi3, kpi4 =  st.columns(4)
                with kpi1:
                    st.markdown(f"<h5 style = 'text-align: center; color: red;'>Absenteesim Rate</h5>", unsafe_allow_html= True)
                    st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{int(monthly_absenteeism['% Absenteeism'].mean())} %</h4>", unsafe_allow_html= True)
                    with st.expander("Absenteesim Rate Formula"):
                        st.latex(r'''
                        =\left(\frac{Σ(Absent Days)}{Σ(Working Days)}\right) *100
                        ''')
                with kpi2:
                    st.markdown(f"<h5 style = 'text-align: center; color: red;'>Turnover Rate</h5>", unsafe_allow_html= True)
                    st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{int(MainEmpHistory['%Turnover Rate'].mean())} %</h4>", unsafe_allow_html= True)
                    with st.expander("Turnover Rate Formula"):
                        st.latex(r'''
                        =\left(\frac{Σ(Resigned)}{Σ(Working)}\right) *100
                        ''')
                with kpi3:
                    st.markdown(f"<h5 style = 'text-align: center; color: red;'>Hire Rate</h5>", unsafe_allow_html= True)
                    st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{int(MainEmpHistory['Hire Rate'].mean())} %</h4>", unsafe_allow_html= True)
                    with st.expander("Hire Rate Formula"):
                        st.latex(r'''
                        =\left(\frac{Σ(NewHired)}{Σ(Working)}\right) *100
                        ''')
                with kpi4:
                    st.markdown(f"<h5 style = 'text-align: center; color: red;'>Net Hire Ratio</h5>", unsafe_allow_html= True)
                    st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{(MainEmpHistory['Net Hire Ratio'].mean())} %</h4>", unsafe_allow_html= True)
                    with st.expander("Net Hire Ratio Formula"):
                        st.latex(r'''
                        =\left(\frac{Σ(New Hired)}{Σ(Resigned)}\right)
                        ''')
                st.markdown('<hr/>', unsafe_allow_html = True)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"<h5 style = 'text-align: center; color: red;'>Avg Age</h5>", unsafe_allow_html= True)
                    st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{int(MainEmpStatus[MainEmpStatus['EmployeeStatus']=='Working']['Age'].mean())} Years</h4>", unsafe_allow_html= True)
                with col2:
                    st.markdown(f"<h5 style = 'text-align: center; color: red;'>Avg Work Duration</h5>", unsafe_allow_html= True)
                    st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{int(MainEmpStatus['work_duration'].mean()/30)} Months</h4>", unsafe_allow_html= True)
                with col3:
                    st.markdown(f"<h5 style = 'text-align: center; color: red;'>Avg Working Hours</h5>", unsafe_allow_html= True)
                    st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{int(main_df['present_time_in_company'].mean())} Hours</h4>", unsafe_allow_html= True)
                st.markdown('<hr/>', unsafe_allow_html = True)

                emp_hist_instance = EDA(MainEmpHistory)
                col1, col2 = st.columns(2)
                col1.plotly_chart(emp_hist_instance.area_chart(categories='Month', values = '%Turnover Rate', title = 'Monthly Turnover Rate', unit = "%", sort_by = 'month_num'))
                col2.plotly_chart(emp_hist_instance.area_chart(categories='Month', values = 'Hire Rate', title = 'Monthly Hire Rate', unit = "%", sort_by = 'month_num'))
                
                col1, col2 = st.columns(2)
                col1.plotly_chart(emp_hist_instance.area_chart(categories='Month', values = 'Net Hire Ratio', title = 'Monthly Net Hire Ratio', unit = "%", sort_by = 'month_num'))
                monthly_abs_inst = EDA(monthly_absenteeism)
                col2.plotly_chart(monthly_abs_inst.area_chart(categories='Month', values = '% Absenteeism', title = 'Monthly Absenteeism', unit = "%", sort_by = 'month_num'))
                # 'NewHire',
                MainEmpHistory = MainEmpHistory.rename(columns = {'Terminated':'Resigned'})
                emp_hist_instance = EDA(MainEmpHistory)
                st.plotly_chart(emp_hist_instance.stack_or_group_chart(categories='Month', values =['Working','Resigned', 'Maternity', 'month_num'], sort_by = 'month_num', drop_column = 'month_num',
                                    barmode='stack',orientation='v',aggfunc='mean', width = 1100, height = 500, title = 'Month wise Employee Status'))
                
                st.subheader("Dataset")
                MainEmpHistory = MainEmpHistory.drop(columns=['month_num'])
                AgGrid(MainEmpHistory)
                df_xlsx = helper.to_excel(MainEmpHistory)
                st.download_button(label='📥 Download Dataset',
                                        data=df_xlsx ,
                                        file_name= 'EmpHistorySummary.xlsx')
                #userManagement.app_logger(username, "HR Operations")
            except Exception as e:
                raise e

    def render_abs_analysis(self, username):
        st.write(fh.format_st_button(), unsafe_allow_html=True)
        st.markdown(hover_size(), unsafe_allow_html=True)
        MainEmpStatus, EmpAtt, MainEmpHistory, emp_id, date, department, designation, marital_status, gender, year = get_hr_vars()
        with st.form(key = "hr_form1"):
            col1, col2, col3, col4 =  st.columns(4)
            with col1:
                st.markdown("**Start Date :**")
                start_date = st.date_input('', pd.to_datetime(min(date)))
            with col2:
                st.markdown("**End Date :**")
                end_date = st.date_input('', pd.to_datetime(max(date)))
            with col3:
                st.markdown("**Employee ID :**")
                emp_id_selection = st.multiselect('',  emp_id, default='All Employees')
            with col4:
                st.markdown("**Gender :**")
                gender_selection = st.multiselect('',  gender, default='All Genders')

            col1, col2, col3, col4 =  st.columns(4)
            with col1:
                st.markdown("**Departments :**")
                department_selection = st.multiselect('',  department, default='All Departments')
            with col2:
                st.markdown("**Designation :**")
                designation_selection = st.multiselect('',  designation, default='All Designations')
            with col3:
                st.markdown("**Year :**")
                year_selection = st.selectbox('',  year)
            with col4:
                st.markdown("**Marital Status :**")
                m_status_selection = st.multiselect('',  marital_status, default='All Status')
            st.markdown('<hr/>', unsafe_allow_html = True)
            st.form_submit_button(label = '📈 Build Dashboard')
            
        if emp_id_selection == ["All Employees"]:
            emp_id_selection = emp_id
        if department_selection ==["All Departments"]:
            department_selection = department
        if designation_selection ==["All Designations"]:
            designation_selection = designation
        if m_status_selection ==["All Status"]:
            m_status_selection = marital_status
        if gender_selection == ["All Genders"]:
            gender_selection = gender

        (main_df, MainEmpStatus, MainEmpHistory, monthly_absenteeism, absenteeism_by_age, absenteeism_by_position,
                absenteeism_by_department, absenteeism_by_gender,absenteeism_by_marital_status, absenteeism_by_day_of_week, absenteeism_combined)= hr_helper.hr_data_prep(MainEmpStatus, EmpAtt, MainEmpHistory, start_date, end_date, emp_id_selection, 
                                                                                                                    department_selection, designation_selection, m_status_selection, gender_selection, year_selection)
        
        if isinstance (main_df, pd.DataFrame) and len(main_df)>0:
            try:
                abs_instance = EDA(monthly_absenteeism)
                
                col1, col2 = st.columns(2)
                col1.plotly_chart(abs_instance.area_chart(categories='Month', values = '% Absenteeism', title = 'Monthly Absenteeism Rate', unit = "%", sort_by = 'month_num'))
                absenteeism_by_day_inst = EDA(absenteeism_by_day_of_week)
                col2.plotly_chart(absenteeism_by_day_inst.area_chart(categories='Day Of The Week', values = '% Absenteeism', unit = "%",
                                                                    sort_by ='WeekDayNum', title = 'Day of the week wise Absenteeism'))

                col1, col2 = st.columns(2)
                by_age_instance = EDA(absenteeism_by_age)
                col1.plotly_chart(by_age_instance.stack_or_group_chart(categories='age_group', values = ['% Absenteeism'], unit = "%", orientation ='h', title = 'Age Group wise Absenteeism'))
                col2.plotly_chart(by_age_instance.piechart(categories='age_group', values = 'Absenteeism',  width = 450, height = 500, title = "Age Group wise Absenteeism Ratio"))
                position_instance = EDA(absenteeism_by_position)
                st.plotly_chart(position_instance.stack_or_group_chart(categories='Position', values = ['% Absenteeism'], height = 500, width = 1150, ascending = False,
                                                                    sort_by = '% Absenteeism', unit = "%", orientation ='v', title = 'Designation wise Absenteeism'))
                
                col1, col2 = st.columns(2)
                gender_instance = EDA(absenteeism_by_gender)
                col1.plotly_chart(gender_instance.stack_or_group_chart(categories='Gender', values = ['% Absenteeism'], unit = "%", orientation ='h', title = 'Gender wise Absenteeism'))
                col2.plotly_chart(gender_instance.piechart(categories='Gender', values = 'Absenteeism',  width = 450, height = 500, title = "Gender wise Absenteeism Ratio"))

                deparment_instance = EDA(absenteeism_by_department)
                st.plotly_chart(deparment_instance.stack_or_group_chart(categories='Department', values = ['% Absenteeism'], unit = "%", orientation ='v', height = 500, width = 1150,
                                                                        ascending = False, sort_by = '% Absenteeism',  title = 'Department wise Absenteeism'))
                col1, col2 = st.columns(2)
                marriage_instance = EDA(absenteeism_by_marital_status)
                col1.plotly_chart(marriage_instance.stack_or_group_chart(categories='MaritalStatus', values = ['% Absenteeism'], unit = "%", orientation ='h', sort_by = '% Absenteeism',
                                                                    title = 'Marital-status wise Absenteeism'))
                col2.plotly_chart(marriage_instance.piechart(categories='MaritalStatus', values = 'Absenteeism', title = "Marital-status Absenteeism Ratio"))

                st.subheader("Dataset")
                MainEmpHistory = MainEmpHistory.drop(columns=['month_num'])
                AgGrid(absenteeism_combined)
                df_xlsx = helper.to_excel(absenteeism_combined)
                st.download_button(label='📥 Download Dataset',
                                        data=df_xlsx ,
                                        file_name= 'AbsenteeismSummary.xlsx')
                #userManagement.app_logger(username, "Absenteeism Analysis")
            except Exception as e:
                raise e

    def render_stay_duration(self, username):
        st.write(fh.format_st_button(), unsafe_allow_html=True)
        st.markdown(hover_size(), unsafe_allow_html=True)
        MainEmpStatus, EmpAtt, MainEmpHistory, emp_id, date, department, designation, marital_status, gender, year = get_hr_vars()

        with st.form(key = "hr_form2"):
            col1, col2, col3, col4 =  st.columns(4)
            with col1:
                st.markdown("**Start Date :**")
                start_date = st.date_input('', pd.to_datetime(min(date)))
            with col2:
                st.markdown("**End Date :**")
                end_date = st.date_input('', pd.to_datetime(max(date)))
            with col3:
                st.markdown("**Employee ID :**")
                emp_id_selection = st.multiselect('',  emp_id, default='All Employees')
            with col4:
                st.markdown("**Gender :**")
                gender_selection = st.multiselect('',  gender, default='All Genders')

            col1, col2, col3, col4 =  st.columns(4)
            with col1:
                st.markdown("**Departments :**")
                department_selection = st.multiselect('',  department, default='All Departments')
            with col2:
                st.markdown("**Designation :**")
                designation_selection = st.multiselect('',  designation, default='All Designations')
            with col3:
                st.markdown("**Year :**")
                year_selection = st.selectbox('',  year)
            with col4:
                st.markdown("**Marital Status :**")
                m_status_selection = st.multiselect('',  marital_status, default='All Status')
            st.markdown('<hr/>', unsafe_allow_html = True)
            st.form_submit_button(label = '📈 Build Dashboard')
            
        if emp_id_selection == ["All Employees"]:
            emp_id_selection = emp_id
        if department_selection ==["All Departments"]:
            department_selection = department
        if designation_selection ==["All Designations"]:
            designation_selection = designation
        if m_status_selection ==["All Status"]:
            m_status_selection = marital_status
        if gender_selection == ["All Genders"]:
            gender_selection = gender

        (main_df, MainEmpStatus, MainEmpHistory, monthly_absenteeism, absenteeism_by_age, absenteeism_by_position,
                absenteeism_by_department, absenteeism_by_gender,absenteeism_by_marital_status, absenteeism_by_day_of_week, absenteeism_combined)= hr_helper.hr_data_prep(MainEmpStatus, EmpAtt, MainEmpHistory, start_date, end_date, emp_id_selection, 
                                                                                                                    department_selection, designation_selection, m_status_selection, gender_selection, year_selection)

        if isinstance (main_df, pd.DataFrame) and len(main_df)>0:
            try:
                stay_by_age, stay_by_department, stay_by_position, stay_by_gender = hr_helper.get_workduration_df(main_df)
                age_instance = EDA(stay_by_age)
                department_instance = EDA(stay_by_department)
                position_instance = EDA(stay_by_position)
                gender_instance = EDA(stay_by_gender)
                col1, col2 = st.columns(2)
                col1.plotly_chart(age_instance.stack_or_group_chart(categories='age_group', values = ['StayDuration'], orientation = 'h', title = 'Age group wise Work-Duration', unit = "Months"))
                col2.plotly_chart(gender_instance.stack_or_group_chart(categories='Gender', values = ['StayDuration'], orientation = 'h', title = 'Gender wise Work-Duration', unit = "Months"))
                
                st.plotly_chart(department_instance.stack_or_group_chart(categories='Department', values = ['StayDuration'], sort_by = 'StayDuration', ascending = False, title = 'Department wise Work-Duration', height = 500, width = 1150, unit = "Months"))
                st.plotly_chart(position_instance.stack_or_group_chart(categories='Position', values = ['StayDuration'], sort_by = 'StayDuration', ascending = False, title = 'Designation wise Work-Duration', height = 500, width = 1150, unit = "Months"))
                

                #userManagement.app_logger(username, "Employee Stay Analysis")
            except Exception as e:
                raise e



    def render_hr_lw(self, username):
        try:    
            st.markdown(hover_size(), unsafe_allow_html=True)
            MainEmpStatus, EmpAtt, MainEmpHistory, emp_id, date, department, designation, marital_status, gender, year = get_hr_vars()
            recent_day = EmpAtt['AttDate'].max().strftime("%d %b, %Y")
            EmpAtt = EmpAtt[EmpAtt['AttDate'] == recent_day ]
            st.header(f'Attendance On {recent_day}')
            lwd_department, lwd_position, lwd = hr_helper.main_df_for_lwd(MainEmpStatus, EmpAtt)
        
            #counts = MainEmpStatus["EmployeeStatus"].value_counts()
            #maternity = counts[counts.index == 'Maternity'].values[0]
            #after_maternity = counts[counts.index == 'After maternity'].values[0]
            #befor_maternity = counts[counts.index == 'Before maternity'].values[0]
            #total_activate = counts[counts.index == 'Working'].values[0]
            total_active = len(lwd)
            
            total_working = total_active + lwd['Before Maternity'].sum() + lwd['After Maternity'].sum() + lwd['Maternity'].sum()
            st.markdown('<br>', unsafe_allow_html = True)
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>Working Employees</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{total_active}</h4>", unsafe_allow_html= True)
            with col2:
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>Present</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{int(lwd['Present'].sum())}</h4>", unsafe_allow_html= True)
            with col3:
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>Absent</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{int(lwd['Absent'].sum())}</h4>", unsafe_allow_html= True)
            col1, col2, col3 =  st.columns(3)

            with col1:
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>On Maternity</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{int(lwd['Maternity'].sum())}</h4>", unsafe_allow_html= True)
            with col2:
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>Before Maternity</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{int(lwd['Before Maternity'].sum())}</h4>", unsafe_allow_html= True)
            with col3:
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>After Maternity</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{int(lwd['After Maternity'].sum())}</h4>", unsafe_allow_html= True)
            st.markdown('<br>', unsafe_allow_html = True)
            dep_instance = EDA(lwd_department)
            st.plotly_chart(dep_instance.stack_or_group_chart(categories='Department', values =['Present','Absent', 'Maternity', 'BeforeMaternity', 'AfterMaternity'],
                        barmode='stack', sort_by = 'Present', ascending = False , orientation='v',aggfunc='mean', width = 1100, height = 500, title = 'Department-wise Attandance'))

            position_instance = EDA(lwd_position)
            st.plotly_chart(position_instance.stack_or_group_chart(categories='Position', values =['Absent', 'Maternity', 'BeforeMaternity', 'AfterMaternity'],
                        barmode='stack', sort_by = 'Absent', ascending = False , orientation='v',aggfunc='mean', width = 1100, height = 500, title = ' Designation-wise Attandance'))

            st.subheader("Dataset")
            MainEmpHistory = MainEmpHistory.drop(columns=['month_num'])
            AgGrid(lwd)
            df_xlsx = helper.to_excel(lwd)
            st.download_button(label='📥 Download Dataset',
                                    data=df_xlsx ,
                                    file_name= f'Attendance On {recent_day}.xlsx')
            #userManagement.app_logger(username, "Attandance Today")
        except Exception as e:
            raise e



    def render_medical_analysis(self, username):
        try:
            st.write(fh.format_st_button(), unsafe_allow_html=True)
            st.markdown(hover_size(), unsafe_allow_html=True)
            MainEmpStatus, EmpAtt, MainEmpHistory, emp_id, date, department, designation, marital_status, gender, year = get_hr_vars()
            start_date = pd.to_datetime(min(date))
            end_date = pd.to_datetime(max(date))
            MainMedical, emp_id_health, department_health, month_health, year_health = get_medical_vars()
            #MainEmpStatus = self.MainEmpStatus[['EmployeeID', 'age_group']]
            #MainMedical = pd.merge(MainMedical, MainEmpStatus, how = 'left', on = 'EmployeeID')
            
            with st.form(key = "hr_form_medical"):
                col1, col2, col3 =  st.columns(3)
                with col1:
                    st.markdown("**Employee ID :**")
                    emp_id_selection = st.multiselect('',  emp_id_health, default='All Employees')

                with col2:
                    st.markdown("**Departments :**")
                    department_selection = st.multiselect('',  department_health, default='All Departments')
                
                with col3:
                    st.markdown("**Gender :**")
                    gender_selection = st.multiselect('',  gender, default='All Genders')
                    
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown("**Marital Status :**")
                    m_status_selection = st.multiselect('',  marital_status, default='All Status')
                
                with col2:
                    st.markdown("**Month :**")
                    month_selection = st.multiselect('',  month_health, default='All Months')

                with col3:
                    st.markdown("**Year :**")
                    year_selection = st.selectbox('',  year_health)
                
                st.markdown('<hr/>', unsafe_allow_html = True)
                st.form_submit_button(label = '📈 Build Dashboard')

            if m_status_selection ==["All Status"]:
                m_status_selection = marital_status
            if gender_selection == ["All Genders"]:
                gender_selection = gender
            if emp_id_selection == ['All Employees']:
                emp_id_selection = emp_id_health
            if month_selection == ['All Months']:
                month_selection = month_health
            if department_selection == ['All Departments']:
                department_selection = department_health
            
            (main_df, MainEmpStatus, MainEmpHistory, monthly_absenteeism, absenteeism_by_age, absenteeism_by_position,
                    absenteeism_by_department, absenteeism_by_gender,absenteeism_by_marital_status, absenteeism_by_day_of_week, absenteeism_combined)= hr_helper.hr_data_prep(MainEmpStatus, EmpAtt, MainEmpHistory, start_date, end_date, emp_id, 
                                                                                                                        department, designation, m_status_selection, gender_selection, year_selection)
            
            MainMedical, monthly, department_wise, heat_matrix, gender_wise, age_group_wise, marital_status_wise = hr_helper.prep_health_data(MainMedical, MainEmpStatus, emp_id_selection, department_selection , year_selection, month_selection)
            st.markdown('<br>', unsafe_allow_html = True)
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>Monthly Avg Visits</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{int(monthly['TotalVisits'].mean())}</h4>", unsafe_allow_html= True)
                with st.expander("Monthly Avg Visits Formula"):
                    st.latex(r'''
                    =\left(\frac{Σ(Visits)}{Σ(Months)}\right)
                    ''')
            with col2:
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>Monthly Unique Visitors</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{int(monthly['Employees'].mean())}</h4>", unsafe_allow_html= True)
                with st.expander("Monthly Unique Visitors Formula"):
                    st.latex(r'''
                    =\left(\frac{Σ(Employees)}{Σ(Months)}\right)
                    ''')
            with col3:
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>Avg Medicine Consumption</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{int(monthly['avg_medicine_consumption'].mean())}</h4>", unsafe_allow_html= True)
                with st.expander("Avg Medicine Consumption Formula"):
                    st.latex(r'''
                    =\left(\frac{Σ(Medicine)}{Σ(UniqueEmployeeVisits)}\right)
                    ''')

            monthly_instance = EDA(monthly)
            col1, col2 = st.columns(2)
            col1.plotly_chart(monthly_instance.area_chart(categories='Month', values = 'avg_medicine_consumption', title = 'Avg Medicine Consumption', sort_by = 'month_num'))
            
            col2.plotly_chart(monthly_instance.bar_line(categories='Month', values = ['Employees', 'TotalVisits', 'month_num'],
                                drop_column = 'month_num', title = 'Total and Unique Visitors', sort_by = 'month_num'))

            col1, col2 = st.columns(2)
            gender_instance = EDA(gender_wise)
            col1.plotly_chart(gender_instance.barchart(categories = 'Gender',values = 'avg_medicine_consumption', aggfunc='mean', orientation='h', title = ' Gender wise Avg Medicine Consumption'))
            col2.plotly_chart(gender_instance.piechart(categories='Gender', values = 'TotalVisits',  width = 450, height = 500, title = "Proportion of Visits"))

            col1, col2 = st.columns(2)
            department_instance = EDA(department_wise)
            col1.plotly_chart(department_instance.barchart(categories = 'Department',values = 'avg_medicine_consumption', sort_by = 'avg_medicine_consumption', aggfunc='mean',
                                width = 450, height = 500, orientation='h', title = 'Department wise Avg Medicine Consumption'))
            #col2.plotly_chart(department_instance.stack_or_group_chart(categories='Department', values = ['Employees', 'TotalVisits'], orientation = 'h',
            #                     width = 450, height = 500, title = 'Total and Unique Visitors', ascending = False,  sort_by = 'TotalVisits'))
            col2.plotly_chart(department_instance.piechart(categories='Department', values = 'TotalVisits',  width = 450, height = 500, title = "Proportion of Visits"))

            col1, col2 = st.columns(2)
            age_group_instance = EDA(age_group_wise)
            col1.plotly_chart(age_group_instance.barchart(categories = 'age_group',values = 'avg_medicine_consumption', sort_by = 'avg_medicine_consumption', aggfunc='mean',
                                width = 450, height = 500, orientation='h', title = 'Age wise Avg Medicine Consumption'))
            #col2.plotly_chart(department_instance.stack_or_group_chart(categories='Department', values = ['Employees', 'TotalVisits'], orientation = 'h',
            #                     width = 450, height = 500, title = 'Total and Unique Visitors', ascending = False,  sort_by = 'TotalVisits'))
            col2.plotly_chart(age_group_instance.piechart(categories='age_group', values = 'TotalVisits',  width = 450, height = 500, title = "Proportion of Visits"))

            
            matrix_instance = EDA(heat_matrix)
            st.plotly_chart(matrix_instance.pareto_chart(categories = 'Medicine', values ='Count',
                            width = 1100, height = 500, title = "Pareto Chart of Medicine Consumption"))
            
            col1, col2 = st.columns(2)
            col1.plotly_chart(matrix_instance.heatmap(index = "Department",  columns="Medicine", values='Count',
                            width = 450, height = 500, title = "Heatmap of Medicine Consumption"))
            medical_df_instance = EDA(MainMedical)
            col2.plotly_chart(medical_df_instance.combined_corr(x_values='Age', y_values = 'Total Medicine',
                        color='Gender',
                        hover_name='Gender', 
                        width = 600, height = 500,))

            col1, col2 = st.columns(2)
            marital_status_instance = EDA(marital_status_wise)
            col1.plotly_chart(marital_status_instance.barchart(categories = 'MaritalStatus',values = 'avg_medicine_consumption', sort_by = 'avg_medicine_consumption', aggfunc='mean',
                                width = 450, height = 500, orientation='h', title = 'Marital Status wise Avg Medicine Consumption'))
            #col2.plotly_chart(department_instance.stack_or_group_chart(categories='Department', values = ['Employees', 'TotalVisits'], orientation = 'h',
            #                     width = 450, height = 500, title = 'Total and Unique Visitors', ascending = False,  sort_by = 'TotalVisits'))
            col2.plotly_chart(marital_status_instance.piechart(categories='MaritalStatus', values = 'TotalVisits',  width = 450, height = 500, title = "Proportion of Visits"))

            st.subheader("Dataset")
            AgGrid(MainMedical)
            df_xlsx = helper.to_excel(MainMedical)
            st.download_button(label='📥 Download Dataset',
                                    data=df_xlsx ,
                                    file_name= 'EmployeeHealthData.xlsx')
            #userManagement.app_logger(username, "Employee Health Analysis")
        except Exception as e:
            raise(e)
            #st.error("Not a valid selection, please try again")
    
    def render_performance_report(self, username):
        try:
            st.write(fh.format_st_button(), unsafe_allow_html=True)
            st.markdown(hover_size(), unsafe_allow_html=True)
            MainEmpStatus, EmpAtt, MainEmpHistory, emp_id, date, department, designation, marital_status, gender, year = get_hr_vars()
            emp_code_list = MainEmpStatus['EmployeeID'].unique().tolist()
            col1, col2 =  st.columns(2)
            with col1:
                st.markdown("**Employee Code :**")
                emp_code_selection = st.selectbox('',  emp_code_list)
                MainEmpStatus = MainEmpStatus[MainEmpStatus['EmployeeID'] == emp_code_selection]
                st.markdown(f"<h5 style = 'text-align: left; color: red;'>Complete Name</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: left; color: blue;'>{MainEmpStatus['FullName'].values[0]}</h4>", unsafe_allow_html= True)
                st.markdown(f"<h5 style = 'text-align: left; color: red;'>Status</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: left; color: blue;'>{MainEmpStatus['EmployeeStatus'].values[0]}</h4>", unsafe_allow_html= True)
                st.markdown(f"<h5 style = 'text-align: left; color: red;'>Age</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: left; color: blue;'>{MainEmpStatus['Age'].values[0]} Years</h4>", unsafe_allow_html= True)

            with col2:
                try:
                    worker_images_dir = os.path.join("static","worker_images")
                    worker_code = str(emp_code_selection) + ".jpg"
                    full_path_to_image = os.path.join(os.getcwd(),worker_images_dir, worker_code)
                    image = Image.open(full_path_to_image)
                    new_image = image.resize((420, 480))
                    st.image(new_image, caption='Employee Profile Picture')
                except:
                    st.markdown('<br><br/>', unsafe_allow_html = True)
                    st.markdown('<br><br/>', unsafe_allow_html = True)
                    st.error("Yikes, Employee Profile Picture is NOT Available 🤦‍♂️")

            st.markdown('<br><br/>', unsafe_allow_html = True)
            col1, col2, col3, col4 =  st.columns(4)

            try:
                dob = (pd.to_datetime(MainEmpStatus['Birthday'].values[0])).strftime('%d %b, %Y')
            except:
                dob = None
            
            try:
                hire_date = (pd.to_datetime(MainEmpStatus['HireDate'].values[0])).strftime('%d %b, %Y')
            except:
                hire_date = None

            with col1:
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>Date of Birth</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{dob}</h4>", unsafe_allow_html= True)
                
            with col2:
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>Native Country</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{MainEmpStatus['NativeCountry'].values[0]}</h4>", unsafe_allow_html= True)
            
            with col3:
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>Hire Date</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{hire_date}</h4>", unsafe_allow_html= True)
            with col4:
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>Gender</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{MainEmpStatus['Gender'].values[0]}</h4>", unsafe_allow_html= True)
            
            st.markdown('<br><br/>', unsafe_allow_html = True)
            col1, col2, col3, col4 =  st.columns(4)

            try:
                id_issue_date = (pd.to_datetime(MainEmpStatus['ID_Issue_Date'].values[0])).strftime('%d %b, %Y')
            except:
                id_issue_date = None

            with col1:
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>ID Number</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{MainEmpStatus['ID_Number'].values[0]}</h4>", unsafe_allow_html= True)
                
            with col2:
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>ID Issue Date</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{id_issue_date}</h4>", unsafe_allow_html= True)
            
            with col3:
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>Ethnic Name</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{MainEmpStatus['EthnicName'].values[0]}</h4>", unsafe_allow_html= True)
            with col4:
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>District</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{MainEmpStatus['DistrictNameEN'].values[0]}</h4>", unsafe_allow_html= True)

            st.markdown('<br><br/>', unsafe_allow_html = True)
            col1, col2, col3, col4 =  st.columns(4)

            with col1:
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>Address</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{MainEmpStatus['ResidentAdd'].values[0]}</h4>", unsafe_allow_html= True)
                
            with col2:
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>Province</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{(MainEmpStatus['ProvinceName'].values[0])}</h4>", unsafe_allow_html= True)
            
            with col3:
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>Ward</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{MainEmpStatus['WardName'].values[0]}</h4>", unsafe_allow_html= True)
            with col4:
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>Education</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{MainEmpStatus['Education'].values[0]}</h4>", unsafe_allow_html= True)

            st.markdown('<br><br/>', unsafe_allow_html = True)
            col1, col2, col3, col4 =  st.columns(4)

            with col1:
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>Social Number</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{MainEmpStatus['SocialNo'].values[0]}</h4>", unsafe_allow_html= True)
                
            with col2:
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>Division</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{(MainEmpStatus['Division'].values[0])}</h4>", unsafe_allow_html= True)
            
            with col3:
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>Department</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{MainEmpStatus['Department'].values[0]}</h4>", unsafe_allow_html= True)
            with col4:
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>Designation</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{MainEmpStatus['Position'].values[0]}</h4>", unsafe_allow_html= True)

            st.markdown('<br><br/>', unsafe_allow_html = True)
            col1, col2, col3, col4 =  st.columns(4)

            with col1:
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>Mobile Number</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{MainEmpStatus['MobilePhone'].values[0]}</h4>", unsafe_allow_html= True)
                
            with col2:
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>Email</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{MainEmpStatus['Email'].values[0]}</h4>", unsafe_allow_html= True)
            
            with col3:
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>Marital Status</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{MainEmpStatus['MaritalStatus'].values[0]}</h4>", unsafe_allow_html= True)
            with col4:
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>Work Duration</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{(MainEmpStatus['exp_in_comp'].values[0])//30} Months</h4>", unsafe_allow_html= True)
            #userManagement.app_logger(username, f"Emp Profile for {emp_code_selection}")
        except Exception as e:
            st.error(f"Sorry {str.title(username)}, Not a valid selection, please try again")
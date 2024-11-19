
from st_aggrid import AgGrid
import pandas as pd
import numpy as np
import streamlit as st
from common import sqlDBManagement , MongoDBManagement
from dotenv import load_dotenv
import os 
from common.helper import get_month_number
load_dotenv()

HR_DB=os.getenv("HR_DB")
HR_DB_USR=os.getenv("HR_DB_USR")
HR_DB_HOST=os.getenv("HR_DB_HOST")
HR_DB_PASS=os.getenv("HR_DB_PASS")
MONGO_STR = os.getenv("MONGO_CONN_STR")

@st.experimental_singleton(show_spinner=False)
def get_hr_db():
    hr_db = sqlDBManagement(HR_DB_HOST, HR_DB_USR, HR_DB_PASS, HR_DB)
    return hr_db

@st.experimental_memo(ttl = 10000, show_spinner=False)
def get_medical_data():
    mongoClient = MongoDBManagement(conn_string = MONGO_STR)
    return mongoClient.getDataFrameOfCollection('hr_db','tblMainMedical')

@st.experimental_memo(ttl = 10000, show_spinner=False)
def get_df_from_db(query):
    hr_db= get_hr_db()
    df = hr_db.getDataFramebyQuery(query)
    return df

@st.experimental_memo(ttl = 10000, show_spinner=False)
def medical_data():
    hr_db= get_hr_db()
    MainMedical = hr_db.getDataFramebyQuery("SELECT * FROM tblMainMedical;")
    return MainMedical

def get_hr_data():
    MainEmpStatus = get_df_from_db("SELECT * FROM MainEmpStatus;")
    MainEmpStatus = MainEmpStatus.drop(columns=['BirthPlace'])
    MainEmpStatus = MainEmpStatus[MainEmpStatus['Department'] != 'New employee']
    EmpAtt = get_df_from_db("SELECT * FROM EmpAtt;")
    MainEmpHistory = get_df_from_db("SELECT * FROM MainEmpHistory")
    return MainEmpStatus, EmpAtt, MainEmpHistory

@st.experimental_memo( ttl = 10000, show_spinner=False)
def get_month_by_date_range(sdate, edate):
    d_range = pd.date_range(pd.to_datetime(sdate),pd.to_datetime(edate),freq='d')
    temp_date_dataframe = pd.DataFrame(columns=['date'])
    temp_date_dataframe['date'] = d_range
    temp_date_dataframe['month'] = temp_date_dataframe['date'].dt.month_name().str.slice(stop=3)
    months_list = temp_date_dataframe['month'].unique().tolist()
    del temp_date_dataframe
    return months_list

@st.experimental_memo(ttl = 10000, show_spinner=False)
def main_df_for_lwd(MainEmpStatus, EmpAtt):
    lwd = pd.merge(EmpAtt, MainEmpStatus, how = 'left', on= 'EmployeeID')
    lwd['Present'] = np.where((lwd['AttStart'].notnull()) & (lwd['EmployeeStatus'] == 'Working') , 1, 0)
    lwd['Absent'] = np.where((lwd['AttStart'].isnull()) & (~lwd['EmployeeStatus'].isin(["Before maternity", "After maternity", "Maternity"]) ), 1, 0)
    
    lwd['Maternity'] = np.where((lwd['EmployeeStatus'] == 'Maternity'), 1, 0)
    lwd['Before Maternity'] = np.where((lwd['EmployeeStatus'] == 'Before maternity'), 1, 0)
    lwd['After Maternity'] = np.where((lwd['EmployeeStatus'] == 'After maternity'), 1, 0)
    lwd_department = lwd.groupby(['Department'], as_index = False).agg(
                Present = pd.NamedAgg('Present', 'sum'),
                Absent = pd.NamedAgg('Absent', 'sum'),
                Maternity = pd.NamedAgg('Maternity', 'sum'),
                BeforeMaternity = pd.NamedAgg('Before Maternity', 'sum'),
                AfterMaternity = pd.NamedAgg('After Maternity', 'sum')
                )
    lwd_position = lwd.groupby(['Position'], as_index = False).agg(
                Present = pd.NamedAgg('Present', 'sum'),
                Absent = pd.NamedAgg('Absent', 'sum'),
                Maternity = pd.NamedAgg('Maternity', 'sum'),
                BeforeMaternity = pd.NamedAgg('Before Maternity', 'sum'),
                AfterMaternity = pd.NamedAgg('After Maternity', 'sum')
                )
    return lwd_department, lwd_position, lwd

def get_age_group(df):
    age_min = df['Age'].min()
    age_max = df['Age'].max()
    
    try:
        age_buckets = np.arange(age_min, age_max, 7, dtype=int).tolist()
        age_buckets_labels = [str(age_buckets[i])+"-"+str(age_buckets[i + 1])
                        for i in range(len(age_buckets) - 1)]
        df['age_group'] = pd.cut(x=df['Age'], bins=age_buckets, labels=age_buckets_labels)
        return df
    except ValueError:
        def get_group(x):
            if x <= 20:
                return "0-20"
            elif x <= 40:
                return "21-40"
            elif x <= 60:
                return "41-60"
            elif x <= 80:
                return "61-80"
            elif x <= 100:
                return "Not Reconized"+str(x)
        df['age_group'] = df['Age'].apply(get_group) 
        return df

@st.cache(suppress_st_warning=True, allow_output_mutation=True, show_spinner=False, ttl=10000)
def hr_data_prep(MainEmpStatus, EmpAtt, MainEmpHistory, start_date, end_date, emp_id_selection, department_selection, designation_selection, m_status_selection, gender_selection, year_selection, pdf_cronJob = None):
    try:
        MainEmpStatus = get_age_group(MainEmpStatus)
        main_df = pd.merge(EmpAtt, MainEmpStatus, how="left", on='EmployeeID')
        if pdf_cronJob:
            mask = (main_df['AttDate'].astype('datetime64').dt.date.between(start_date, end_date))
        else:
            mask = (main_df['AttDate'].astype('datetime64').dt.date.between(start_date, end_date)) & (main_df['Year'] == year_selection) & (main_df['EmployeeID'].isin(emp_id_selection)) & (main_df['Gender'].isin(gender_selection)) & (main_df['Department'].isin(department_selection)) & (main_df['Position'].isin(designation_selection)) & (main_df['MaritalStatus'].isin(m_status_selection))
        main_df = main_df[mask]

        mask = (MainEmpStatus['MaritalStatus'].isin(m_status_selection)) & (MainEmpStatus['Gender'].isin(gender_selection))
        MainEmpStatus = MainEmpStatus[mask]
        month_list = get_month_by_date_range(start_date, end_date)
        MainEmpHistory = MainEmpHistory[(MainEmpHistory['Year'] == year_selection) & (MainEmpHistory['Month'].isin(month_list))]
              
        main_df['present_time_in_company'] = (main_df['AttEnd'] - main_df['AttStart']).dt.total_seconds().div(3600).round(2)

        MainEmpHistory['%Turnover Rate'] = round((MainEmpHistory['Terminated']/MainEmpHistory['Working'])*100, 2)
        MainEmpHistory['Net Hire Ratio'] = np.where(MainEmpHistory['Terminated'] > 0, round((MainEmpHistory['NewHire']/MainEmpHistory['Terminated'])*100, 2),  0)
        MainEmpHistory['Hire Rate'] = round((MainEmpHistory['NewHire']/MainEmpHistory['Working'])*100, 2)

        main_df['Month'] = main_df['AttDate'].dt.month_name().str.slice(stop = 3)
        main_df['month_num'] = main_df['AttDate'].dt.month
        main_df['weekday_num'] = main_df['AttDate'].dt.weekday
        #main_df['Year'] = main_df['AttDate'].dt.year
        main_df['Absenteeism'] = np.where((main_df['AttStart'].isnull()) & (main_df['AttEnd'].isnull()) & (main_df['date_of_resg'].isnull()), 1, 0)
        
        monthly_absenteeism = main_df.groupby('Month', as_index=False).agg(
                        Absenteeism = pd.NamedAgg('Absenteeism', aggfunc='sum'),
                        TotalDays = pd.NamedAgg('Absenteeism', aggfunc='count'),
                        month_num = pd.NamedAgg('month_num', pd.Series.mode)
                ).sort_values(by='month_num')
        monthly_absenteeism['% Absenteeism'] = round((monthly_absenteeism['Absenteeism']/monthly_absenteeism['TotalDays'])*100, 2)
        
        absenteeism_by_age = main_df.groupby('age_group', as_index=False).agg(
                        Absenteeism = pd.NamedAgg('Absenteeism', aggfunc='sum'),
                        TotalDays = pd.NamedAgg('Absenteeism', aggfunc='count')
                )
        absenteeism_by_age['age_group'] = absenteeism_by_age['age_group'].astype(str)
        absenteeism_by_age['% Absenteeism'] = round((absenteeism_by_age['Absenteeism']/absenteeism_by_age['TotalDays'])*100, 2)
        absenteeism_by_age.dropna(subset=['% Absenteeism'], inplace=True)

        absenteeism_by_position = main_df.groupby('Position', as_index=False).agg(
                            Absenteeism = pd.NamedAgg('Absenteeism', aggfunc='sum'),
                            TotalDays = pd.NamedAgg('Absenteeism', aggfunc='count')
                )
        absenteeism_by_position['% Absenteeism'] = round((absenteeism_by_position['Absenteeism']/absenteeism_by_position['TotalDays'])*100, 2)

        absenteeism_by_department = main_df.groupby('Department', as_index=False).agg(
                            Absenteeism = pd.NamedAgg('Absenteeism', aggfunc='sum'),
                            TotalDays = pd.NamedAgg('Absenteeism', aggfunc='count')
                )
        absenteeism_by_department['% Absenteeism'] = round((absenteeism_by_department['Absenteeism']/absenteeism_by_department['TotalDays'])*100, 2)
        absenteeism_by_department = absenteeism_by_department.sort_values(by='% Absenteeism', ascending= False )

        absenteeism_by_gender = main_df.groupby(['Gender'], as_index=False).agg(
                            Absenteeism = pd.NamedAgg('Absenteeism', aggfunc='sum'),
                            TotalDays = pd.NamedAgg('Absenteeism', aggfunc='count')
                )
        absenteeism_by_gender['% Absenteeism'] = round((absenteeism_by_gender['Absenteeism']/absenteeism_by_gender['TotalDays'])*100, 2)
        absenteeism_by_gender = absenteeism_by_gender.sort_values(by='% Absenteeism', ascending= False )

        absenteeism_combined = main_df.groupby(['Gender', 'Department', 'Position', 'MaritalStatus'], as_index=False).agg(
                            Absenteeism = pd.NamedAgg('Absenteeism', aggfunc='sum'),
                            TotalDays = pd.NamedAgg('Absenteeism', aggfunc='count')
                )
        
        absenteeism_by_marital_status = main_df.groupby(['MaritalStatus'], as_index=False).agg(
                        Absenteeism = pd.NamedAgg('Absenteeism', aggfunc='sum'),
                        TotalDays = pd.NamedAgg('Absenteeism', aggfunc='count')
            )
        absenteeism_by_marital_status['% Absenteeism'] = round((absenteeism_by_marital_status['Absenteeism']/absenteeism_by_marital_status['TotalDays'])*100, 2)
        absenteeism_by_marital_status = absenteeism_by_marital_status.sort_values(by='% Absenteeism', ascending= False )

        absenteeism_by_day_of_week = main_df.groupby(['Day Of The Week'], as_index=False).agg(
                            Absenteeism = pd.NamedAgg('Absenteeism', aggfunc='sum'),
                            TotalDays = pd.NamedAgg('Absenteeism', aggfunc='count'),
                            WeekDayNum = pd.NamedAgg('weekday_num', aggfunc=pd.Series.mode)
                ).sort_values(by= 'WeekDayNum')
        absenteeism_by_day_of_week['% Absenteeism'] = round((absenteeism_by_day_of_week['Absenteeism']/absenteeism_by_day_of_week['TotalDays'])*100, 2)

        absenteeism_combined['% Absenteeism'] = round((absenteeism_combined['Absenteeism']/absenteeism_combined['TotalDays'])*100, 2)
        absenteeism_combined.drop(columns = ['Absenteeism', 'TotalDays'], inplace = True)
        absenteeism_combined = absenteeism_combined.sort_values(by='% Absenteeism', ascending= False )
        
        return (main_df, MainEmpStatus, MainEmpHistory, monthly_absenteeism, absenteeism_by_age, absenteeism_by_position,
                absenteeism_by_department, absenteeism_by_gender,absenteeism_by_marital_status, absenteeism_by_day_of_week, absenteeism_combined)

    except  Exception as e:
        raise e
        st.error('Oh Dear, Something went wrong with the selection, please make a new selection carefully')

@st.cache(suppress_st_warning=True, allow_output_mutation=True, show_spinner=False, ttl=10000)
def prep_health_data(MainMedical, MainEmpStatus, emp_id_selection, department_selection , year_selection, month_selection):
    mask = (MainMedical['Year'] == year_selection) & (MainMedical['Department'].isin(department_selection)) & (MainMedical['EmployeeID'].isin(emp_id_selection)) & (MainMedical['Month'].isin(month_selection))
    MainMedical  = MainMedical[mask]
    MainMedical['Visits'] = MainMedical['Visits'].apply(lambda x : 1 if (x == "") | (x == None) | (pd.isna(x)) else x )
    MainMedical = MainMedical.astype({'Visits': float})
    MainMedical['Total Medicine'] =  MainMedical.iloc[:, 7:].sum(axis = 1)
    MainMedical['Department'] = MainMedical['Department'].replace(
                                            to_replace=['', ' LINE 6', 'LINE 4 ', 'LINE 6 ', 'CANTEN', 'MACHANIC','LINE 10 ', 'LINE 5 ','LNE 5',
                                                        'MACHENIC', 'TPR ', 'PREPARATION', ' QC', 'LINE 2 ', 'JUKI ', 'JUKI', 'ZUKI', 'LINE 1`', 'SECURYTI'],
                                            value = [np.nan,'LINE 6', 'LINE 4', 'LINE 6', 'CLEAN', 'MECHANIC', 'MECHANIC','LINE 10', 'LINE 5','LINE 5',
                                                    'TPR', 'PREPERATION', 'QC', 'LINE 2', 'AUTOMATION', 'AUTOMATION', 'AUTOMATION', 'LINE 1', 'SECURITY'])
    MainMedical['EmployeeID'] = MainMedical['EmployeeID'].replace(to_replace = ['OFICE', 'oFFICE'], value = ['OFFICE', 'OFFICE'])
    monthly = MainMedical.groupby('Month', as_index=False).agg(
            Employees = pd.NamedAgg('EmployeeID', aggfunc=pd.Series.nunique),
            TotalVisits = pd.NamedAgg('Visits', aggfunc='sum'),
            TotalMedicine = pd.NamedAgg('Total Medicine', aggfunc='sum')
        )
    monthly['month_num'] = monthly['Month'].apply(get_month_number)
    monthly['avg_medicine_consumption'] = round(monthly['TotalMedicine'] / monthly['Employees'], 2) 
    department_wise = MainMedical.groupby('Department', as_index=False).agg(
            Employees = pd.NamedAgg('EmployeeID', aggfunc=pd.Series.nunique),
            TotalVisits = pd.NamedAgg('Visits', aggfunc='sum'),
            TotalMedicine = pd.NamedAgg('Total Medicine', aggfunc='sum')
        )
    department_wise['avg_medicine_consumption'] = round(department_wise['TotalMedicine'] / department_wise['Employees'], 2)
    department_wise = department_wise.sort_values(by = 'avg_medicine_consumption', ascending= False)
    department_wise = department_wise.head(16)

    val_cols = MainMedical.iloc[:, 7:-1].columns.tolist()
    id_col = ['Department']
    cols_vals =  val_cols + id_col 
    df_to_melt = MainMedical[cols_vals]
    heat_matrix = df_to_melt.melt(id_vars= id_col, value_vars = cols_vals, var_name='Medicine', value_name = 'Count')
    heat_matrix = heat_matrix[heat_matrix['Count'].notnull()]

    MainMedical['EmployeeID'] = MainMedical['EmployeeID'].astype(str)
    MainEmpStatus = MainEmpStatus[['EmployeeID', 'Gender', 'age_group', 'MaritalStatus', 'Age']]
    MainMedical = pd.merge(MainMedical, MainEmpStatus, on = 'EmployeeID', how = 'left')

    gender_wise = MainMedical.groupby('Gender', as_index=False).agg(
            Employees = pd.NamedAgg('EmployeeID', aggfunc=pd.Series.nunique),
            TotalVisits = pd.NamedAgg('Visits', aggfunc='sum'),
            TotalMedicine = pd.NamedAgg('Total Medicine', aggfunc='sum')
        )
    gender_wise['avg_medicine_consumption'] = round(gender_wise['TotalMedicine'] / gender_wise['Employees'], 2)
    age_group_wise = MainMedical.groupby('age_group', as_index=False).agg(
            Employees = pd.NamedAgg('EmployeeID', pd.Series.nunique),
            TotalVisits = pd.NamedAgg('Visits', aggfunc='sum'),
            TotalMedicine = pd.NamedAgg('Total Medicine', aggfunc='sum')
        )
    age_group_wise['avg_medicine_consumption'] = round(age_group_wise['TotalMedicine'] / age_group_wise['Employees'], 2)
    age_group_wise = age_group_wise[age_group_wise['avg_medicine_consumption'].notnull()]
    age_group_wise['age_group'] = age_group_wise['age_group'].astype(str)
    marital_status_wise = MainMedical.groupby('MaritalStatus', as_index=False).agg(
            Employees = pd.NamedAgg('EmployeeID', pd.Series.nunique),
            TotalVisits = pd.NamedAgg('Visits', aggfunc='sum'),
            TotalMedicine = pd.NamedAgg('Total Medicine', aggfunc='sum')
        )
    marital_status_wise['avg_medicine_consumption'] = round(marital_status_wise['TotalMedicine'] / marital_status_wise['Employees'], 2)

    return MainMedical, monthly, department_wise, heat_matrix, gender_wise, age_group_wise, marital_status_wise

#@st.experimental_memo(ttl = 10000, show_spinner=False)
def get_workduration_df(main_df):
    main_df['work_duration'] = main_df['work_duration']/30
    #main_df['age_group'] = main_df['age_group'].astype(str)
    stay_by_age = main_df.groupby('age_group', as_index=False).agg(
            StayDuration = pd.NamedAgg('work_duration', aggfunc='mean')
    ).sort_values(by='StayDuration', ascending=False)

    stay_by_department = main_df.groupby('Department', as_index=False).agg(
            StayDuration = pd.NamedAgg('work_duration', aggfunc='mean')
    ).sort_values(by='StayDuration', ascending=False)


    stay_by_position = main_df.groupby('Position', as_index=False).agg(
            StayDuration = pd.NamedAgg('work_duration', aggfunc='mean')
    ).sort_values(by='StayDuration', ascending=False)

    stay_by_gender = main_df.groupby('Gender', as_index=False).agg(
            StayDuration = pd.NamedAgg('work_duration', aggfunc='mean')
    ).sort_values(by='StayDuration', ascending=False)

    return stay_by_age, stay_by_department, stay_by_position, stay_by_gender

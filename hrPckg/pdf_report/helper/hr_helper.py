import pandas as pd
import numpy as np 

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

def hr_data_prep(MainEmpStatus, EmpAtt, MainEmpHistory, start_date, end_date):
    try:
        MainEmpStatus = get_age_group(MainEmpStatus)
        main_df = pd.merge(EmpAtt, MainEmpStatus, how="left", on='EmployeeID')
        mask = (main_df['AttDate'].astype('datetime64').dt.date.between(start_date, end_date))
        main_df = main_df[mask]
              
        main_df['present_time_in_company'] = (main_df['AttEnd'] - main_df['AttStart']).dt.total_seconds().div(3600).round(2)

        MainEmpHistory['%Turnover Rate'] = round((MainEmpHistory['Terminated']/MainEmpHistory['Working'])*100, 2)
        MainEmpHistory['Net Hire Ratio'] = round((MainEmpHistory['NewHire']/MainEmpHistory['Terminated'])*100, 2)
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
    except Exception as e:
        raise e

def main_df_for_lwd(lwd: pd.DataFrame):
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


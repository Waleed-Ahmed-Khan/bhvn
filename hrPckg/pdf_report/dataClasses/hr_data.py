#import sys
#sys.path.append("..")

import pandas as pd
from dataclasses import dataclass
#from ....hrPckg import hr_helper
import numpy as np
from functools import lru_cache
from helper import get_age_group
from functools import cached_property
from datetime import datetime
import pytz
@dataclass
class HRdataSource:
    EmpAtt : pd.DataFrame
    MainEmpStatus : pd.DataFrame
    MainEmpHistory : pd.DataFrame

    def filter_EmpAtt(self, date = None) -> pd.DataFrame:
        if date is None:
            date = self.unique_dates
        self.EmpAtt = self.EmpAtt.query(
            "AttDate in @date"
        )
        return self.EmpAtt

    @property
    def current_year_vn(self) -> str:
        return datetime.now(pytz.timezone("Asia/Jakarta")).strftime("%Y")

    def filter_MainEmpHistory(self, year: int= None) -> pd.DataFrame:
        if year is None:
            year = self.current_year_vn
        print(self.MainEmpHistory['Year'].value_counts())
        self.MainEmpHistory = self.MainEmpHistory.query(
            "Year in @year"
        )
        return self.MainEmpHistory
    @property
    def unique_dates(self) -> list[pd.Timestamp]:
        return self.EmpAtt['AttDate'].unique() 
    
    @property
    def unique_years(self) -> list[int]:
        return self.MainEmpHistory['Year'].unique().tolist()

    def get_main_df(self, date: list[pd.DataFrame], year : list[int]):
        self.filter_EmpAtt(date)
        self.filter_MainEmpHistory(year)
        self.MainEmpStatus = get_age_group(self.MainEmpStatus)
        self.main_df = pd.merge(self.EmpAtt, self.MainEmpStatus, how="left", on='EmployeeID')

    def preprocess_data(self, date : list[pd.DataFrame], year : list[int]):
        self.get_main_df(date, year)
        self.main_df['present_time_in_company'] = (self.main_df['AttEnd'] - self.main_df['AttStart']).dt.total_seconds().div(3600).round(2)

        self.MainEmpHistory['%Turnover Rate'] = round((self.MainEmpHistory['Terminated']/self.MainEmpHistory['Working'])*100, 2)
        self.MainEmpHistory['Net Hire Ratio'] = np.where(self.MainEmpHistory['Terminated'] > 0, round((self.MainEmpHistory['NewHire']/self.MainEmpHistory['Terminated'])*100, 2),  0)
        self.MainEmpHistory['Hire Rate'] = round((self.MainEmpHistory['NewHire']/self.MainEmpHistory['Working'])*100, 2)

        self.main_df['Month'] = self.main_df['AttDate'].dt.month_name().str.slice(stop = 3)
        self.main_df['month_num'] = self.main_df['AttDate'].dt.month
        self.main_df['weekday_num'] = self.main_df['AttDate'].dt.weekday
        #self.main_df['Year'] = self.main_df['AttDate'].dt.year
        self.main_df['Absenteeism'] = np.where((self.main_df['AttStart'].isnull()) & (self.main_df['AttEnd'].isnull()) & (self.main_df['date_of_resg'].isnull()), 1, 0)
        
        self.monthly_absenteeism = self.main_df.groupby('Month', as_index=False).agg(
                        Absenteeism = pd.NamedAgg('Absenteeism', aggfunc='sum'),
                        TotalDays = pd.NamedAgg('Absenteeism', aggfunc='count'),
                        month_num = pd.NamedAgg('month_num', pd.Series.mode)
                ).sort_values(by='month_num')
        self.monthly_absenteeism['% Absenteeism'] = round((self.monthly_absenteeism['Absenteeism']/self.monthly_absenteeism['TotalDays'])*100, 2)
        
        self.absenteeism_by_age = self.main_df.groupby('age_group', as_index=False).agg(
                        Absenteeism = pd.NamedAgg('Absenteeism', aggfunc='sum'),
                        TotalDays = pd.NamedAgg('Absenteeism', aggfunc='count')
                )
        self.absenteeism_by_age['age_group'] = self.absenteeism_by_age['age_group'].astype(str)
        self.absenteeism_by_age['% Absenteeism'] = round((self.absenteeism_by_age['Absenteeism']/self.absenteeism_by_age['TotalDays'])*100, 2)
        self.absenteeism_by_age.dropna(subset=['% Absenteeism'], inplace=True)

        self.absenteeism_by_position = self.main_df.groupby('Position', as_index=False).agg(
                            Absenteeism = pd.NamedAgg('Absenteeism', aggfunc='sum'),
                            TotalDays = pd.NamedAgg('Absenteeism', aggfunc='count')
                )
        self.absenteeism_by_position['% Absenteeism'] = round((self.absenteeism_by_position['Absenteeism']/self.absenteeism_by_position['TotalDays'])*100, 2)

        self.absenteeism_by_department = self.main_df.groupby('Department', as_index=False).agg(
                            Absenteeism = pd.NamedAgg('Absenteeism', aggfunc='sum'),
                            TotalDays = pd.NamedAgg('Absenteeism', aggfunc='count')
                )
        self.absenteeism_by_department['% Absenteeism'] = round((self.absenteeism_by_department['Absenteeism']/self.absenteeism_by_department['TotalDays'])*100, 2)
        self.absenteeism_by_department = self.absenteeism_by_department.sort_values(by='% Absenteeism', ascending= False )

        self.absenteeism_by_gender = self.main_df.groupby(['Gender'], as_index=False).agg(
                            Absenteeism = pd.NamedAgg('Absenteeism', aggfunc='sum'),
                            TotalDays = pd.NamedAgg('Absenteeism', aggfunc='count')
                )
        self.absenteeism_by_gender['% Absenteeism'] = round((self.absenteeism_by_gender['Absenteeism']/self.absenteeism_by_gender['TotalDays'])*100, 2)
        self.absenteeism_by_gender = self.absenteeism_by_gender.sort_values(by='% Absenteeism', ascending= False )

        self.absenteeism_combined = self.main_df.groupby(['Gender', 'Department', 'Position', 'MaritalStatus'], as_index=False).agg(
                            Absenteeism = pd.NamedAgg('Absenteeism', aggfunc='sum'),
                            TotalDays = pd.NamedAgg('Absenteeism', aggfunc='count')
                )
        
        self.absenteeism_by_marital_status = self.main_df.groupby(['MaritalStatus'], as_index=False).agg(
                        Absenteeism = pd.NamedAgg('Absenteeism', aggfunc='sum'),
                        TotalDays = pd.NamedAgg('Absenteeism', aggfunc='count')
            )
        self.absenteeism_by_marital_status['% Absenteeism'] = round((self.absenteeism_by_marital_status['Absenteeism']/self.absenteeism_by_marital_status['TotalDays'])*100, 2)
        self.absenteeism_by_marital_status = self.absenteeism_by_marital_status.sort_values(by='% Absenteeism', ascending= False )

        self.absenteeism_by_day_of_week = self.main_df.groupby(['Day Of The Week'], as_index=False).agg(
                            Absenteeism = pd.NamedAgg('Absenteeism', aggfunc='sum'),
                            TotalDays = pd.NamedAgg('Absenteeism', aggfunc='count'),
                            WeekDayNum = pd.NamedAgg('weekday_num', aggfunc=pd.Series.mode)
                ).sort_values(by= 'WeekDayNum')
        self.absenteeism_by_day_of_week['% Absenteeism'] = round((self.absenteeism_by_day_of_week['Absenteeism']/self.absenteeism_by_day_of_week['TotalDays'])*100, 2)

        self.absenteeism_combined['% Absenteeism'] = round((self.absenteeism_combined['Absenteeism']/self.absenteeism_combined['TotalDays'])*100, 2)
        self.absenteeism_combined.drop(columns = ['Absenteeism', 'TotalDays'], inplace = True)
        self.absenteeism_combined = self.absenteeism_combined.sort_values(by='% Absenteeism', ascending= False )
        
        return (self.main_df, self.MainEmpStatus, self.MainEmpHistory, self.monthly_absenteeism, self.absenteeism_by_age, self.absenteeism_by_position,
                self.absenteeism_by_department, self.absenteeism_by_gender, self.absenteeism_by_marital_status, self.absenteeism_by_day_of_week, self.absenteeism_combined)
import sys
sys.path.append("...")
from dataClasses import HRdataSource
from loader import LoadData
import pandas as pd
import datetime, pytz, os
#from hrPckg import hr_helper
from vizpool.interactive import EDA
from pathlib import Path
from helper import main_df_for_lwd
from appLogger import AppLogger, get_logger
import config as CONFIG

class CreatePlots:
    def __init__(self, logs_file: os.path):
        self.dl = LoadData()
        self.logs_file = logs_file
        self.logger = get_logger(self.logs_file)
        #self.logger = AppLogger()

    def get_hr_data(self, dates: list[pd.Timestamp] = None, year: list[int] = None):
        #with open(self.logs_file, 'a+') as file:
        self.logger.info('Getting HR data executing "get_hr_data" method of "CreatePlots" class')
        hr_data = HRdataSource(self.dl.EmpAtt , self.dl.MainEmpStatus ,self.dl.MainEmpHistory)
        (self.main_df, self.MainEmpStatus, self.MainEmpHistory, self.monthly_absenteeism, self.absenteeism_by_age, 
        self.absenteeism_by_position,self.absenteeism_by_department, self.absenteeism_by_gender, self.absenteeism_by_marital_status, 
        self.absenteeism_by_day_of_week, self.absenteeism_combined)  = hr_data.preprocess_data(dates, year)
        
    @property
    def today_vn(self) -> str:
        return datetime.datetime.now(pytz.timezone("Asia/Jakarta")).strftime("%d %b, %Y")

    @property
    def last_week_dates(self) -> list[pd.Timestamp]:
        return pd.date_range(end=self.today_vn, periods=7).tolist()

    @property
    def datelist_today(self) -> list[pd.Timestamp]:
        return pd.date_range(end=self.today_vn, periods=1).tolist()

    @property
    def current_year_vn(self) -> int:
        return int(datetime.datetime.now(pytz.timezone("Asia/Jakarta")).strftime("%Y"))
    
    @property
    def visuals_dir(self) -> str:
        #path = Path("generate_plots.py")
        #complete_path = path.resolve()
        visuals_dir = os.path.join(str(Path(os.path.join("hrPckg", "pdf_report")).resolve().absolute()), 'Plots')
        os.makedirs(visuals_dir, exist_ok=True)
        return visuals_dir
    
    def get_dates_list(self, sdate: pd.Timestamp, edate: pd.Timestamp) -> list[pd.Timestamp]:
        return pd.date_range(sdate, edate ,freq='d')
        

    def attendance_today(self):
        self.get_hr_data(self.datelist_today)
        print(self.main_df['AttDate'].nunique())
        self.logger.info('Creating Attendance today plots, executing "attendance_today" method of "CreatePlots" class ...')
        lwd_department, lwd_position, lwd = main_df_for_lwd(self.main_df)

        self.total_active = len(lwd)
        if self.total_active == 0:

            self.logger.info(f'!!!!! Terminating the job as there is no data available today ({self.today_vn}) !!!!!')
            LoadData(load_data=False).remove_csvs()
            sys.exit(0)

        self.before_maternity = lwd['Before Maternity'].sum()
        self.after_maternity = lwd['After Maternity'].sum()
        self.maternity =  lwd['Maternity'].sum()
        self.present = lwd['Present'].sum()
        self.absent = lwd['Absent'].sum()


        fig = EDA(lwd_department).stack_or_group_chart(categories='Department', values =['Present','Absent', 'Maternity', 'BeforeMaternity', 'AfterMaternity'],
                        barmode='stack', sort_by = 'Present', ascending = False , orientation='v',aggfunc='mean', width = 1100, height = 500, title = f'Department-wise Complete Data on {self.today_vn}')
        att_today_visuals = os.path.join(self.visuals_dir, "att_today_plots")
        os.makedirs(att_today_visuals, exist_ok=True)
        fig.write_image(os.path.join(att_today_visuals, "dep_wise_complete_data.png"))

        fig = EDA(lwd_department).stack_or_group_chart(categories='Department', values =['Absent', 'Maternity', 'BeforeMaternity', 'AfterMaternity'],
                        barmode='stack', sort_by = 'Absent', ascending = False , orientation='v',aggfunc='mean', width = 1100, height = 500, title = f'Department-wise Attandance Status on {self.today_vn}')
        fig.write_image(os.path.join(att_today_visuals, "dep_wise_att_status.png"))
        lwd_position = lwd_position[(lwd_position['Absent'] > 0) | (lwd_position['Maternity'] > 0) | (lwd_position['BeforeMaternity'] > 0) | (lwd_position['AfterMaternity'] > 0)]
        fig = EDA(lwd_position).stack_or_group_chart(categories='Position', values =['Absent', 'Maternity', 'BeforeMaternity', 'AfterMaternity'],
                        barmode='stack', sort_by = 'Absent', ascending = True , orientation='h',aggfunc='mean', width = 1100, height = 1000, title = f' Designation-wise Attandance on {self.today_vn}')
        fig.write_image(os.path.join(att_today_visuals, "designation_wise_att.png"))
        
        self.logger.info('Successfully created Attandence today plots, executed "attendance_today" method of "CreatePlots" class')
        return self.total_active, self.present, self.absent, self.maternity, self.before_maternity, self.after_maternity, lwd_department, lwd_position
    
    def abs_plots(self):
        
        self.logger.info('Creating Absenteeism plots, executing "abs_plots" method of "CreatePlots" class ...')
        dates = self.get_dates_list(sdate = CONFIG.OPERATIONS_START_DATE, edate = CONFIG.OPERATIONS_END_DATE)
        self.get_hr_data(dates, [self.current_year_vn])
        print(self.main_df['AttDate'].nunique())

        absenteeism_visuals = os.path.join(self.visuals_dir, "absenteeism_plots")
        os.makedirs(absenteeism_visuals, exist_ok=True)

        abs_instance = EDA(self.monthly_absenteeism)
        fig = abs_instance.area_chart(categories='Month', values = '% Absenteeism', title = f'Monthly Absenteeism Rate ({self.current_year_vn})', unit = "%", sort_by = 'month_num')
        fig.write_image(os.path.join(absenteeism_visuals, "monthly_absenteeism.png"))
        
        absenteeism_by_day_inst = EDA(self.absenteeism_by_day_of_week)
        fig = absenteeism_by_day_inst.area_chart(categories='Day Of The Week', values = '% Absenteeism', unit = "%",
                                                            sort_by ='WeekDayNum', title = f'Day of the week wise Absenteeism')
        fig.write_image(os.path.join(absenteeism_visuals, "daily_absenteeism.png"))

        by_age_instance = EDA(self.absenteeism_by_age)
        fig = by_age_instance.stack_or_group_chart(categories='age_group', values = ['% Absenteeism'], unit = "%", orientation ='h', title = 'Age Group wise Absenteeism')
        fig.write_image(os.path.join(absenteeism_visuals, "age_group_wise_abs.png"))
        fig = by_age_instance.piechart(categories='age_group', values = 'Absenteeism',  width = 450, height = 500, title = "Age Group wise Absenteeism Ratio")
        fig.write_image(os.path.join(absenteeism_visuals, "age_group_wise_abs_ratio.png"))

        gender_instance = EDA(self.absenteeism_by_gender)
        fig = gender_instance.stack_or_group_chart(categories='Gender', values = ['% Absenteeism'], unit = "%", orientation ='h', title = 'Gender wise Absenteeism')
        fig.write_image(os.path.join(absenteeism_visuals, "gender_wise_abs.png"))
        fig = gender_instance.piechart(categories='Gender', values = 'Absenteeism',  width = 450, height = 500, title = "Gender wise Absenteeism Ratio")
        fig.write_image(os.path.join(absenteeism_visuals, "gender_wise_abs_ratio.png"))

        deparment_instance = EDA(self.absenteeism_by_department)
        fig = deparment_instance.stack_or_group_chart(categories='Department', values = ['% Absenteeism'], unit = "%", orientation ='h', height = 1000, width = 1150,
                                                                ascending = True, sort_by = '% Absenteeism',  title = 'Department wise Absenteeism')
        fig.write_image(os.path.join(absenteeism_visuals, "department_wise_abs.png"))

        marriage_instance = EDA(self.absenteeism_by_marital_status)
        fig = marriage_instance.stack_or_group_chart(categories='MaritalStatus', values = ['% Absenteeism'], unit = "%", orientation ='h', sort_by = '% Absenteeism',
                                                            title = 'Marital-status wise Absenteeism')
        fig.write_image(os.path.join(absenteeism_visuals, "marital_status_wise_abs.png"))
        fig = marriage_instance.piechart(categories='MaritalStatus', values = 'Absenteeism', title = "Marital-status Absenteeism Ratio")
        fig.write_image(os.path.join(absenteeism_visuals, "marital_status_wise_abs_ratio.png"))
        self.logger.info('Successfully created Absenteeism plots, executed "abs_plots" method of "CreatePlots" class')

    def operational_plots(self):
        self.logger.info('Creating Operational plots, executing "operational_plots" method of "CreatePlots" class ...')
        dates = self.get_dates_list(sdate = CONFIG.OPERATIONS_START_DATE, edate = CONFIG.OPERATIONS_END_DATE)
        self.get_hr_data(dates, [self.current_year_vn])
        print(self.main_df['AttDate'].nunique())

        operational_visuals = os.path.join(self.visuals_dir, "operational_plots")
        os.makedirs(operational_visuals, exist_ok=True)

        emp_hist_instance = EDA(self.MainEmpHistory)
        print(self.MainEmpHistory.shape)
        print(self.MainEmpHistory)
        if not self.MainEmpHistory.empty:
            fig = emp_hist_instance.area_chart(categories='Month', values = '%Turnover Rate', title = 'Monthly Turnover Rate', unit = "%", sort_by = 'month_num')
            fig.write_image(os.path.join(operational_visuals, "monthly_turnover.png"))
            fig = emp_hist_instance.area_chart(categories='Month', values = 'Hire Rate', title = 'Monthly Hire Rate', unit = "%", sort_by = 'month_num')
            fig.write_image(os.path.join(operational_visuals, "monthly_hire_rate.png"))

            fig = emp_hist_instance.area_chart(categories='Month', values = 'Net Hire Ratio', title = 'Monthly Net Hire Ratio', unit = "%", sort_by = 'month_num')
            fig.write_image(os.path.join(operational_visuals, "monthly_net_hire_ratio.png"))
            monthly_abs_inst = EDA(self.monthly_absenteeism)
            print(self.monthly_absenteeism.shape)
            print(self.monthly_absenteeism)
            fig = monthly_abs_inst.area_chart(categories='Month', values = '% Absenteeism', title = 'Monthly Absenteeism', unit = "%", sort_by = 'month_num')
            fig.write_image(os.path.join(operational_visuals, "monthly_absenteeism.png"))

            fig = emp_hist_instance.stack_or_group_chart(categories='Month', values =['Working','Terminated', 'Maternity', 'NewHire', 'month_num'], sort_by = 'month_num', drop_column = 'month_num',
                                barmode='stack',orientation='v',aggfunc='mean', width = 800, height = 600, title = 'Month wise Employee Summary')
            fig.write_image(os.path.join(operational_visuals, "monthly_emp_summary.png"))

            fig = emp_hist_instance.stack_or_group_chart(categories='Month', values =['Terminated', 'Maternity', 'NewHire', 'month_num'], sort_by = 'month_num', drop_column = 'month_num',
                                barmode='stack',orientation='v',aggfunc='mean', width = 800, height = 600, title = 'Month wise Employee Status')
            fig.write_image(os.path.join(operational_visuals, "monthly_emp_status.png"))
            self.logger.info('Successfully created Operational plots, executed "operational_plots" method of "CreatePlots" class')
        
    def operational_kpis_summary(self) -> zip:
        if self.monthly_absenteeism.empty:
            self.get_hr_data()
        abs_rate = str(int(self.monthly_absenteeism['% Absenteeism'].mean()))+ " %"
        to_rate = str(int(self.MainEmpHistory['%Turnover Rate'].mean()))+" %"
        hire_rate = str(int(self.MainEmpHistory['Hire Rate'].mean()))+ " %"
        net_hire_ratio = str(int(self.MainEmpHistory['Net Hire Ratio'].mean()))+ " %"
        avg_age = str(int(self.MainEmpStatus[self.MainEmpStatus['EmployeeStatus']=='Working']['Age'].mean()))+ " Y"
        avg_word_duration = str(int(self.MainEmpStatus['work_duration'].mean()/30)) + " M"
        #time_in_comp = int(self.main_df['present_time_in_company'].mean())
        summary_zip = zip(["Absenteeism Rate:", "Turnover Rate:", "Hire Rate:", "Net Hire Ratio:", "Avg Age:", "Avg Work Duration:"], 
                        [abs_rate, to_rate, hire_rate, net_hire_ratio, avg_age, avg_word_duration])
        return summary_zip
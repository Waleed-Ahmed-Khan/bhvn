from matplotlib.pyplot import table
import pandas as pd
import numpy as np
import numpy as np
from dbOps import sqlDBManagement
from dotenv import load_dotenv
from appLogger.logger import AppLogger
import datetime, pytz
import os
from pipelineAlerts import Email
from common.helper import get_month_number
load_dotenv()
OLTP_SERVER = os.getenv("SERVER")
OLTP_USER = os.getenv("USER")
OLTP_PASS = os.getenv("PASS")
OLTP_DB = os.getenv("DB")

server = 'SV2021\SQLVIETINSOFT' 
database = 'Paradise_BLH' 
username = 'vts.sa' 
password = 'LuaThieng1@3' 

class HRtoDWH:
    def __init__(self):
        self.oltp = sqlDBManagement(server, username, password, database, dbms="mssql")
        self.olap = sqlDBManagement(OLTP_SERVER, OLTP_USER, OLTP_PASS, OLTP_DB)
        self.date = datetime.datetime.now(pytz.timezone("Asia/Jakarta")).strftime("%m/%d/%Y")
        self.current_time = datetime.datetime.now(pytz.timezone("Asia/Jakarta")).strftime("%H:%M:%S")
        self.logs_file = os.path.join("logs", "pipeline_logs.txt")
        self.logger = AppLogger()
    def get_MainEmpStatus(self):
        
        EmpInfo = self.oltp.getDataFramebyQuery("SELECT * FROM Emp_Info;")
        EmpStatus = self.oltp.getDataFramebyQuery("SELECT * FROM EmpStatus;")
        Empdim = self.oltp.getDataFramebyQuery("SELECT * FROM EmpDim;")
        
        with open(self.logs_file, 'a+') as file:
            self.logger.log(file, "Loaded base dataframes from database successfully")
        
        EmpInfoEmpdim = EmpInfo.merge(Empdim, on= 'EmployeeID')
        MainEmpStatus = pd.merge(EmpInfoEmpdim, EmpStatus,  how='left', left_on=['EmployeeID','EmployeeStatusEN'], right_on = ['EmployeeID','EmployeeStatusEN'])

        MainEmpStatus = MainEmpStatus[['EmployeeID', 'FullName_x', 'MobilePhone', 'Email', 'Birthday','BirthPlace', 'NativeCountry',\
                            'HireDate','SexNameEN', 'ID_Number', 'ID_Issue_Date', 'EthnicNameEN', 'DistrictNameEN', 'ResidentAdd',\
                           'ProvinceNameEN','WardNameEN','EducationalBase', 'SocialNo','EmployeeStatusEN','DivisionNameEN','DepartmentNameEN',\
                           'PositionNameEN','MaritalStatusNameEN', 'ChangedDate']]
        MainEmpStatus.drop_duplicates(subset=['EmployeeID'], keep='last', inplace=True)
        resg_lst = []
        for index, row in MainEmpStatus[['EmployeeStatusEN', 'ChangedDate']].iterrows():
            if row[0] == 'Terminated':
                resg_lst.append(row[1])
            else:
                resg_lst.append(np.nan)
        MainEmpStatus['date_of_resg'] = resg_lst

        from datetime import datetime
        current_date = datetime.today().strftime('%Y-%m-%d')
        current_date = pd.to_datetime(current_date)
        MainEmpStatus['HireDate'] = pd.to_datetime(MainEmpStatus['HireDate'])
        exp_in_comp = []
        for index , row in MainEmpStatus[['date_of_resg','HireDate']].iterrows():
            if pd.isna(row[0]):
                exp_in_comp.append(((current_date- row[1])/pd.Timedelta(1, unit='d')))
            else:
                exp_in_comp.append(np.nan)
        MainEmpStatus['exp_in_comp'] = exp_in_comp

        MainEmpStatus['work_duration'] = (MainEmpStatus['date_of_resg'] - MainEmpStatus['HireDate'])/pd.Timedelta(1, unit='d')
        age =  round(((current_date -  MainEmpStatus['Birthday'])/pd.Timedelta(1,unit='d'))/360, 0)
        MainEmpStatus['Age'] = age
        self.MainEmpStatus = MainEmpStatus.rename(columns={'FullName_x':'FullName', 'SexNameEN':'Gender', 'EthnicNameEN':'EthnicName',
                                                        'EducationalBase':'Education', 'DivisionNameEN':'Division', 'DepartmentNameEN':'Department',
                                                        'PositionNameEN': 'Position', 'EmployeeStatusEN': 'EmployeeStatus',
                                                        'WardNameEN': 'WardName', 'MaritalStatusNameEN':'MaritalStatus', 'ProvinceNameEN': 'ProvinceName'})
        self.MainEmpStatus.sort_values('HireDate', ascending=False)
        with open(self.logs_file, 'a+') as file:
            self.logger.log(file, f"Data Prep for MainEmpStatus Completed with df = {self.MainEmpStatus.shape}")
        
    def filter_holidays(self, df):
        att_dates = df['AttDate'].unique()
        for date in att_dates:
            df_f = df[(df['AttDate']==date)]
            s = df_f.isna().sum()/len(df_f) 
            if s[s.index == 'AttStart'].tolist()[0] > 0.75:
                df = df.drop(df[df['AttDate']==date].index)
        return df

    def get_EmpAtt(self):
        self.EmpAtt = self.oltp.getDataFramebyQuery('''
                 SELECT EmployeeID, AttDate, AttStart, AttEnd, WorkingTime , DATENAME(dw, AttDate) AS "Day Of The Week"
                 FROM tblHasTA
                 WHERE DATENAME(dw, AttDate) != 'Sunday'
                 ORDER BY AttDate DESC;
                 ''')
        with open(self.logs_file, 'a+') as file:
            self.logger.log(file, f"Successfully loaded EmpAtt with shape = {self.EmpAtt.shape}")
        
        self.EmpAtt = self.filter_holidays(self.EmpAtt)
        with open(self.logs_file, 'a+') as file:
            self.logger.log(file, f"Filtered EmpAtt for working days only, current dataframe shape = {self.EmpAtt.shape}")
        
    def get_emp_history(self):
        att_dates = set([str(date).split(' ')[0] for date in self.EmpAtt['AttDate']])
        working_emp_list = []
        for date in att_dates:
            qry = f'''
            DECLARE @FromDate datetime, @ToDate datetime
            -- from day to day: is the period of the month
            SET @FromDate ='{date}'
            SET @ToDate ='{date}'

            select COUNT(EmployeeCodeReal) AS working_emp from dbo.fn_vtblEmployeeList_Bydate(@ToDate,'-1',null) 
            WHERE TerminateDate is null or TerminateDate > @FromDate
            '''
            working_emp = self.oltp.getDataFramebyQuery(qry)
            working_emp_list.append(working_emp["working_emp"][0])
            
        working_emp = pd.DataFrame(zip(att_dates,working_emp_list), columns=['att_dates', 'workingEmp'])
        working_emp['att_dates'] = working_emp['att_dates'].astype('datetime64[ns]')
        
        statusDim = self.oltp.getDataFramebyQuery("SELECT EmployeeStatusID,EmployeeStatusEN  FROM tblEmployeeStatus")
        empStatus = self.oltp.getDataFramebyQuery("select EmployeeID, EmployeeStatusID, ChangedDate from tblEmployeeStatusHistory")
        empStatus = pd.merge(empStatus, statusDim, on="EmployeeStatusID")
        
        EmpHistory = pd.merge(working_emp, empStatus, left_on="att_dates", right_on="ChangedDate")
        EmpHistory = EmpHistory.drop(columns=['att_dates', 'EmployeeStatusID'])
        EmpHistory = EmpHistory.drop(EmpHistory[EmpHistory['EmployeeStatusEN'] == 'Working'].index)

        EmpHistory['Terminated']=[1 if i=='Terminated' else 0 for i in EmpHistory['EmployeeStatusEN']]
        EmpHistory['Maternity']=[1 if i=='Maternity' else 0 for i in EmpHistory['EmployeeStatusEN']]
        EmpHistory['Before maternity']=[1 if i=='Before maternity' else 0 for i in EmpHistory['EmployeeStatusEN']]

        EmpHistory = EmpHistory.drop(columns=['EmployeeStatusEN'])

        EmpHistory['month_num'] = EmpHistory['ChangedDate'].dt.month
        EmpHistory['Month'] = EmpHistory['ChangedDate'].dt.month_name().str.slice(stop=3)
        EmpHistory['Year'] = EmpHistory['ChangedDate'].dt.year

        EmpHistory = EmpHistory.drop(columns=['EmployeeID', 'ChangedDate'])
        
        EmpHistory = EmpHistory.groupby(['Month', 'Year'], as_index= False).agg(
                                    Working = pd.NamedAgg('workingEmp', aggfunc=pd.Series.mode),
                                    Terminated = pd.NamedAgg('Terminated', aggfunc='sum'),
                                    Maternity = pd.NamedAgg('Maternity', aggfunc='sum'),
                                    BeforeMaternity = pd.NamedAgg('Before maternity', aggfunc='sum'),
                                    month_num = pd.NamedAgg('month_num', aggfunc=pd.Series.mode)
                )
        EmpHistory['Working'] = EmpHistory['Working'].apply(lambda x : x[0] if ((str(x).startswith("[")) & (str(x).endswith("]"))) else x )
        return EmpHistory
    
    def get_new_hires(self):
        query = '''
        select "ChangedDate" from tblEmployeeStatusHistory as s 
        where EmployeeStatusID = 0 and not exists (
            select 1 from tblEmployeeStatusHistory as h where h.EmployeeID = s.EmployeeID and h.ChangedDate < s.ChangedDate
        )
        '''
        df_new_hire = self.oltp.getDataFramebyQuery(query)
        df_new_hire["New Hire"] = 1  
        df_new_hire['Month'] = df_new_hire['ChangedDate'].dt.month_name().str.slice(stop=3)
        df_new_hire['Year'] = df_new_hire['ChangedDate'].dt.year
        df_new_hire = df_new_hire.drop('ChangedDate', axis = 1)
        df_new_hire = df_new_hire.groupby(['Month', 'Year'], as_index= False).agg(
                                        NewHire = pd.NamedAgg('New Hire', aggfunc='sum'))
        return df_new_hire
    def __update_tblReportEmployeeInfo(self):
        for year in [2021, 2022]:
            query = f'''
            -- CREATE TABLE tblReportEmployeeInfo (Month varchar(3), Year int, Working int, Terminated int, Maternity int, BeforeMaternity int, NewHire int)
            if object_id('[dbo].[sptblReportEmployeeInfo]') is null
                EXEC ('CREATE PROCEDURE [dbo].[sptblReportEmployeeInfo] as select 1')
            GO
            ALTER PROCEDURE [dbo].[sptblReportEmployeeInfo](@Year int= 2021)
            AS
                
                DELETE tblReportEmployeeInfo WHERE Year = @Year
                SELECT * INTO #ReportEmployeeInfo FROM tblReportEmployeeInfo WHERE 1 = 0

                DECLARE @RunStep int = 1, @ToDate datetime, @FromDate datetime
                WHILE (@RunStep <= 12)
                BEGIN
                    SELECT @FromDate = FromDate,  @ToDate = ToDate FROM dbo.fn_Get_SalaryPeriod(@RunStep, @Year)
                    SELECT EmployeeID, HireDate, TerminateDate, EmployeeStatusID
                    INTO #fn_vtblEmployeeList_Bydate
                    FROM dbo.fn_vtblEmployeeList_Bydate(@ToDate,'-1',NULL) WHERE TerminateDate is null or TerminateDate >= @FromDate

                    IF (GETDATE()> @FromDate)
                    BEGIN 
                    INSERT INTO #ReportEmployeeInfo (Month, Year, Working, Terminated, Maternity, BeforeMaternity, NewHire)
                    SELECT convert(varchar(3), @FromDate, 107), @Year,
                        COUNT(1) as Working,
                        (SELECT COUNT(1) FROM #fn_vtblEmployeeList_Bydate WHERE TerminateDate between @FromDate and @ToDate) as Terminated,
                        (SELECT COUNT(1) FROM #fn_vtblEmployeeList_Bydate WHERE EmployeeStatusID = 1) as Maternity,
                        (SELECT COUNT(1) FROM #fn_vtblEmployeeList_Bydate WHERE EmployeeStatusID = 11) as Maternity,
                        (SELECT COUNT(1) FROM #fn_vtblEmployeeList_Bydate WHERE HireDate between @FromDate and @ToDate) as NewHire
                    FROM #fn_vtblEmployeeList_Bydate
                    WHERE TerminateDate is null
                    END
                    SET @RunStep = @RunStep + 1
                    DROP TABLE #fn_vtblEmployeeList_Bydate
                END
                INSERT INTO tblReportEmployeeInfo (Month,Year,Working,Terminated,Maternity,BeforeMaternity,NewHire) 
                SELECT Month,Year,Working,Terminated,Maternity,BeforeMaternity,NewHire FROM #ReportEmployeeInfo
            GO
            EXEC sptblReportEmployeeInfo 2021
            '''
            self.oltp.executeOperation(query)

    def get_main_emp_history(self):
        #self.__update_tblReportEmployeeInfo()
        #with open(self.logs_file, 'a+') as file:
        #    self.logger.log(file, f"Successfully updated OLAP tblReportEmployeeInfo")
        MainEmpHistory = self.oltp.getDataFramebyQuery("SELECT * FROM tblReportEmployeeInfo;")
        MainEmpHistory['month_num'] = MainEmpHistory['Month'].apply(get_month_number)
        with open(self.logs_file, 'a+') as file:
            self.logger.log(file, f"Successfully loaded the dataframe MainEmpHistory with shape = {MainEmpHistory.shape}")
        return MainEmpHistory
    def __inset_into_remote(self, df, table_name):
        id_count = len(df['EmployeeID'])
        print(f'Rows in OLTP "{table_name}" : {id_count} rows')
        with open(self.logs_file, 'a+') as file:
            self.logger.log(file, f'Rows in OLTP "{table_name}" : {id_count} rows')
        
        id_count_OLAP = self.olap.getDataFramebyQuery(f'''SELECT COUNT(EmployeeID) from {table_name};''')
        id_count_OLAP = id_count_OLAP["COUNT(EmployeeID)"][0]
        print(f'Rows in OLAP "{table_name}" : {id_count_OLAP} rows')
        with open(self.logs_file, 'a+') as file:
            self.logger.log(file, f'Rows in OLAP "{table_name}" : {id_count_OLAP} rows')
        
        if id_count_OLAP == id_count:
            print("No new records, skipping insertion...")
            with open(self.logs_file, 'a+') as file:
                self.logger.log(file, f'No new records for "{table_name}", skipping insertion...')
        else:
            new_record_count = id_count - id_count_OLAP
            new_records = df.head(new_record_count)

            if not new_records.empty:
                try:
                    with open(self.logs_file, 'a+') as file:
                        self.logger.log(file, f'Inserting {new_record_count} new records in "{table_name}"...')
                    print(f"Inserting {new_record_count} new records in {table_name}...")
                    if "AttDate" in new_records.columns.tolist():
                        with open(self.logs_file, 'a+') as file:
                            self.logger.log(file, f'''Attendance Date is "{pd.to_datetime(new_records['AttDate'].unique()[0]).strftime("%m/%d/%Y")}"''')
                    self.olap.saveDataFrameIntoDB(new_records, table_name)
                    with open(self.logs_file, 'a+') as file:
                        self.logger.log(file, f'Successfully inserted {new_record_count} new records in "{table_name}"...')
                    
                except Exception as e:
                    print(f'Something went while inserting the data in {table_name}')
                    raise e
    def __dlt_inset_into_remote(self, df, table_name):
        self.olap.executeOperation(f"DELETE FROM {table_name}")
        with open(self.logs_file, 'a+') as file:
            self.logger.log(file, f"Successfully deleted records from {table_name}")
        if "AttDate" in df.columns.tolist():
            with open(self.logs_file, 'a+') as file:
                self.logger.log(file, f'''Attendance Date is "{pd.to_datetime(df['AttDate'].unique()[0]).strftime("%m/%d/%Y")}"''')
        self.olap.saveDataFrameIntoDB(df, table_name)
        with open(self.logs_file, 'a+') as file:
            self.logger.log(file, f"Inserted new records in {table_name}")
    def run_pipeline(self):
        try:
            self.get_MainEmpStatus()
            self.get_EmpAtt()  
            MainEmpHistory = self.get_main_emp_history()

            self.__dlt_inset_into_remote(MainEmpHistory, "MainEmpHistory")
            self.__dlt_inset_into_remote(self.MainEmpStatus, "MainEmpStatus")
            self.__dlt_inset_into_remote(self.EmpAtt, "EmpAtt")

            with open(self.logs_file, 'a+') as file:
                self.logger.log(file, "******* Job completed sccessfully! *******")
            print("******* Job completed sccessfully! *******")
        except Exception as e:
            with open(self.logs_file, 'a+') as file:
                self.logger.log(file, f"Pipeline Execution failed {self.current_time} on {self.date}, sending email alert...")
            alert = Email()
            alert.pipeline_failure_alert(subject="HR Data Pipeline Failure", error = str(e))
            with open(self.logs_file, 'a+') as file:
                self.logger.log(file, f"Email Sent!")
            raise e
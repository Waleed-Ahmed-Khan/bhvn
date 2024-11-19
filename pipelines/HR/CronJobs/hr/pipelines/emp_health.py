
import pandas as pd
import numpy as np
from dbOps import sqlDBManagement, MongoDBManagement
from dotenv import load_dotenv
from appLogger.logger import AppLogger
from common.helper import get_month_name
import datetime, pytz
import os
from pipelineAlerts import Email
import glob
import datetime 

load_dotenv()
OLTP_SERVER = os.getenv("SERVER")
OLTP_USER = os.getenv("USER")
OLTP_PASS = os.getenv("PASS")
OLTP_DB = os.getenv("DB")
HR_EMP_DATA_DIR = os.getenv("HR_EMP_DATA_DIR")
MONGO_CONN_STR=os.getenv("MONGO_CONN_STR")

class HealthcareDatatoDWH:
    def __init__(self):
        self.olap = sqlDBManagement(OLTP_SERVER, OLTP_USER, OLTP_PASS, OLTP_DB)
        self.mongoClient = MongoDBManagement(conn_string = MONGO_CONN_STR)
        self.date = datetime.datetime.now(pytz.timezone("Asia/Jakarta")).strftime("%m/%d/%Y")
        self.current_time = datetime.datetime.now(pytz.timezone("Asia/Jakarta")).strftime("%H:%M:%S")
        self.logs_file = os.path.join("logs", "emp_health_logs.txt")
        self.logger = AppLogger()
        self.columns = ['Year', 'Month', 'EmployeeID', 'Name', 'Visits', 'Department',
                                      'diagnosis', 'HAPACOL', 'CALCI', 'MG B6', 'CTM', 'EUCAFOR', 'p',
                                      'CARBOMANGO', 'Hapacol sủi', 'Alaxan', 'VTM C 500', 'Multiflul',
                                      'Diclofenac', 'Prednison', 'Cezil', 'Amoxicilin', 'Hamett', 'Loperamid',
                                      'Mutecium-M', 'Omerazol', 'VTM AD', 'Strepsill', 'Tyrotab']

    def _get_file_paths(self):
        self.all_files = glob.glob(HR_EMP_DATA_DIR + "\*\*.xlsx")
        with open(self.logs_file, 'a+') as file:
            self.logger.log(file, f"Loaded the filepath list containing {len(self.all_files)} elements")

    def get_df_from_xlsx(self, filepath):
        try:
            file_ends = filepath[-12:].split(".")[0]
            workbook = pd.ExcelFile(filepath)
            sheets = workbook.sheet_names
            for sheet in sheets:
                try:
                    if sheet.split(" ")[1].replace("|", "-") == file_ends: 
                        df = pd.read_excel(filepath, engine='openpyxl', sheet_name = sheet, header=2).drop(columns = ['STT', 'DATE', 'Tổng'])\
                            .rename(columns = {'MST\nEmp. Code':'EmployeeID', 'Họ và tên\nFull name':'Name',
                                            'Lũy kế\n( Số lần xin thuốc)':'Visits', 'Bộ phận\nDepartment':'Department',
                                            'CHUẨN ĐOÁN':'diagnosis', 'Tyrotab ':'Tyrotab'})
                        df.insert(0, 'Year', file_ends.split("-")[1])
                        df.insert(1, 'Month', file_ends.split("-")[0])
                        df = df.astype({'Month': int})
                        df['Month'] = df['Month'].apply(get_month_name)
                        df = df[df['EmployeeID'].notnull()]
                        return df
                except IndexError:
                    pass
        except:
            return pd.DataFrame(columns= self.columns)
    def _validate_columns(self):
        if  self.main_medical.columns.tolist() == self.columns:
                                      with open(self.logs_file, 'a+') as file:
                                        self.logger.log(file, "Column Names Validated Successfully")
                                      return True 
        else:
            with open(self.logs_file, 'a+') as file:
                self.logger.log(file, "Column names are NOT valid")
            False
    def get_main_medical(self):
        self._get_file_paths()
        self.main_medical = pd.DataFrame()
        for file in self.all_files:
            self.main_medical = pd.concat((self.main_medical, self.get_df_from_xlsx(file)),
                                         ignore_index= True)
        self._get_current_year_month()
        self.main_medical = self.main_medical[(self.main_medical['Month']==self.currentMonth) & (self.main_medical['Year'] == self.currentYear) ]
        with open(self.logs_file, 'a+') as file:
            self.logger.log(file, f"Successfully prepared the df with the shape {self.main_medical.shape}")

    def _get_current_year_month(self):
        self.currentMonth = get_month_name(datetime.datetime.now().month)
        self.currentYear = str(datetime.datetime.now().year)

    def _dlt_inset_into_remote(self, df, table_name):
        query = {"Month":self.currentMonth, "Year":str(self.currentYear)}
        df_from_db = self.mongoClient.getDataFrameOfCollection(db_name='hr_db', collection_name=table_name, query=query)
        with open(self.logs_file, 'a+') as file:
            self.logger.log(file, f'Found {df_from_db.shape[0]} record from db to dlt having current month "{self.currentMonth}" and current year "{self.currentYear}"')
        self.mongoClient.deleteRecords(db_name= "hr_db", collection_name = table_name, query = query)
        with open(self.logs_file, 'a+') as file:
            self.logger.log(file, f'{df_from_db.shape[0]} records deleted successfully having current month "{self.currentMonth}" and current year "{self.currentYear}"')
        self.mongoClient.saveDataFrameIntoCollection(table_name, 'hr_db', df)
        with open(self.logs_file, 'a+') as file:
            self.logger.log(file, f"Inserted {df.shape[0]} new records in {table_name}")

    def run_pipeline(self):
        try:
            self.get_main_medical()
            if self._validate_columns():
                self._dlt_inset_into_remote(self.main_medical, "tblMainMedical")
                with open(self.logs_file, 'a+') as file:
                    self.logger.log(file, "******* Job completed sccessfully! *******")
                print("******* Job completed sccessfully! *******")
            else:
                with open(self.logs_file, 'a+') as file:
                    self.logger.log(file, "!!!!!!!!! Job Failed, could not validate the columns !!!!!!!!!")

        except Exception as e:
            with open(self.logs_file, 'a+') as file:
                self.logger.log(file, f"Pipeline Execution failed {self.current_time} on {self.date}, sending email alert...")
            alert = Email()
            alert.pipeline_failure_alert(subject="Employee Health Data Pipeline Failure", error = str(e))
            with open(self.logs_file, 'a+') as file:
                self.logger.log(file, f"Email Sent!")
            raise e

import sys
sys.path.append(".")
from functools import cached_property
import pandas as pd
from hrPckg import hr_helper
from functools import lru_cache
import os
from pathlib import Path
import shutil
class EmpAttSchema:
    DATE = "AttDate"
    ATT_START = "AttStart"
    ATT_END = "AttEnd"


class LoadData:
    def __init__(self, load_data = True):
        self.CSV_DIR = Path(os.path.join("hrPckg", "pdf_report", "csv_data")).resolve().absolute()
        self.REPORTS_DIR = os.path.join(self.CSV_DIR.parent, "reports")
        os.makedirs(self.CSV_DIR, exist_ok=True)
        MainEmpStatus_path = os.path.join(self.CSV_DIR, "MainEmpStatus.csv")
        EmpAtt_path = os.path.join(self.CSV_DIR, "EmpAtt.csv")
        MainEmpHistory_path = os.path.join(self.CSV_DIR, "MainEmpHistory.csv")
        if load_data:
            try:
                self.MainEmpStatus = pd.read_csv(MainEmpStatus_path)
            except FileNotFoundError:
                self.MainEmpStatus, self.EmpAtt, self.MainEmpHistory = hr_helper.get_hr_data()

                self.MainEmpStatus.to_csv(MainEmpStatus_path, index = False, encoding='utf-8')
                self.EmpAtt.to_csv(EmpAtt_path, index = False, encoding='utf-8') 
                self.MainEmpHistory.to_csv(MainEmpHistory_path, index = False, encoding='utf-8')
                
                self.MainEmpStatus = pd.read_csv(MainEmpStatus_path)

            self.EmpAtt = pd.read_csv(EmpAtt_path, parse_dates=[EmpAttSchema.DATE, EmpAttSchema.ATT_START, EmpAttSchema.ATT_END])
            self.MainEmpHistory = pd.read_csv(MainEmpHistory_path)

    def remove_csvs(self):
        for file in os.scandir(self.CSV_DIR):
            os.remove(file.path)
    def dlt_report(self):
        shutil.rmtree(self.REPORTS_DIR)

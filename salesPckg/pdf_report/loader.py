import sys
sys.path.append(".")
from functools import cached_property
import pandas as pd
from salesPckg import sales_helper
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
        self.CSV_DIR = Path(os.path.join("salesPckg", "pdf_report", "csv_data")).resolve().absolute()
        self.REPORTS_DIR = os.path.join(self.CSV_DIR.parent, "reports")
        os.makedirs(self.CSV_DIR, exist_ok=True)
        self.PLOTS_DIR = os.path.join(self.CSV_DIR.parent, "Plots")
        sales_data_path = os.path.join(self.CSV_DIR, "sales_data.csv")
        #EmpAtt_path = os.path.join(self.CSV_DIR, "EmpAtt.csv")
        #MainEmpHistory_path = os.path.join(self.CSV_DIR, "MainEmpHistory.csv")
        if load_data:
            try:
                self.sales_data = pd.read_csv(sales_data_path, parse_dates=['invoicedate', 'shipdate', 'booking_pdate','booking_rdate', 
                'vesseldate', 'confirmdate', 'duedate', 'ex_bhvn_date', 'bhvnorderentrydate','orderdate'])
            except FileNotFoundError:
                self.sales_data = sales_helper.load_sales_invoice_data()

                #self.MainEmpStatus.to_csv(MainEmpStatus_path, index = False, encoding='utf-8')
                #self.EmpAtt.to_csv(EmpAtt_path, index = False, encoding='utf-8') 
                self.sales_data.to_csv(sales_data_path, index = False, encoding='utf-8')
                
                self.sales_data = pd.read_csv(sales_data_path, parse_dates=['invoicedate', 'shipdate', 'booking_pdate','booking_rdate', 
                'vesseldate', 'confirmdate', 'duedate', 'ex_bhvn_date', 'bhvnorderentrydate','orderdate'])

            #self.EmpAtt = pd.read_csv(EmpAtt_path, parse_dates=[EmpAttSchema.DATE, EmpAttSchema.ATT_START, EmpAttSchema.ATT_END])
            #self.MainEmpHistory = pd.read_csv(MainEmpHistory_path)

    def remove_csvs(self):
        for file in os.scandir(self.CSV_DIR):
            os.remove(file.path)

    def dlt_report(self):
        shutil.rmtree(self.REPORTS_DIR)

    def remove_plots(self):
        if os.path.exists(self.PLOTS_DIR):
            shutil.rmtree(self.PLOTS_DIR)

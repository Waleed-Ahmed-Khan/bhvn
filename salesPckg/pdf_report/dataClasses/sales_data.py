#import sys
#sys.path.append("..")

import pandas as pd
from dataclasses import dataclass
#from ....hrPckg import hr_helper
import datetime, pytz

@dataclass
class SalesDataSource:
    sales_data : pd.DataFrame

    def filter_sales_data(self, date: list[pd.Timestamp] = None, year: list[int]= None) -> pd.DataFrame:
        if date is None:
            date = self.unique_dates
        if year is None:
            year = self.current_year_vn
        self.sales_data = self.sales_data.query(
            "invoicedate in @date and year in @year"
        )
        return self.sales_data

    @property
    def unique_dates(self) -> list[pd.Timestamp]:
        return self.sales_data['invoicedate'].unique() 
    
    @property
    def unique_years(self) -> list[int]:
        return self.sales_data['Year'].unique().tolist()
    
    @property
    def current_year_vn(self) -> int:
        return [int(datetime.datetime.now(pytz.timezone("Asia/Jakarta")).strftime("%Y"))]
    
    def preprocess_data(self, dates : list[pd.Timestamp] = None, year : list[int]= None):
        self.sales_data = self.filter_sales_data(dates, year)
        return self.sales_data
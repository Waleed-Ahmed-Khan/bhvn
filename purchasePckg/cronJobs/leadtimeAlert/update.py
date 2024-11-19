import datetime, pytz
from utils import get_all_pos
from functools import cached_property
import pandas as pd
import config as CONFIG
from common import helper, sqlDBManagement

class Updator:
    def __init__(self):
        self.olap = sqlDBManagement(host = helper.DB_CENT_HOST, username = helper.DB_CENT_USR,
                        password = helper.DB_CENT_PASS, database = helper.DB_CENT_NAME)
    @cached_property
    def all_pos(self) -> pd.DataFrame:
        return get_all_pos()
    
    @cached_property
    def today_vn(self) -> str:
        return datetime.datetime.now(pytz.timezone("Asia/Jakarta")).strftime("%d %b, %Y")

    @property
    def start_date(self) -> pd.Timestamp:
        datee =  datetime.date.today() - datetime.timedelta(CONFIG.PO_UPDATE_DAYS)
        print("............................./////////////////", datee)
        return datee
    def _filter_pos_df(self) -> pd.DataFrame:
        return self.all_pos[self.all_pos["orderdate"] >= self.start_date]

    def dlt_previous_data_olap(self, po):
        
        query = f'''
        DELETE FROM mfgcycle WHERE CustomerPO="{po}"
        '''
        #query = 'DELETE FROM mfgcycle WHERE CustomerPO="2022-123676-1YG"'
        self.olap.executeOperation(query)

    @property
    def pos_to_update(self) -> list[str]:
        return self._filter_pos_df()['ponumber'].unique().tolist()
    
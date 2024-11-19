import os , sys
from pathlib import Path
FILE = Path(__file__).resolve()
ROOT = FILE.parents[3]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT)) 
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative

from common import helper, sqlDBManagement
from dotenv import load_dotenv

load_dotenv()

DB_CENT_NAME=os.getenv("DB_CENT_NAME")
DB_CENT_USR=os.getenv("DB_CENT_USR")
DB_CENT_HOST=os.getenv("DB_CENT_HOST")
DB_CENT_PASS=os.getenv("DB_CENT_PASS")
#print(DB_CENT_HOST, DB_CENT_NAME, DB_CENT_PASS, DB_CENT_USR)

class LoaderOLAP:
    def __init__(self):
        self.olap = sqlDBManagement(host = DB_CENT_HOST, username = DB_CENT_USR,
                            password = DB_CENT_PASS, database = DB_CENT_NAME)

    def loadIntoDB(self, df, tablename):
        self.olap.saveDataFrameIntoDB(df, tablename)
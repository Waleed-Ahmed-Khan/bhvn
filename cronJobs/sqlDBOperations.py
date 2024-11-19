import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

class sqlDBManagement:

    def __init__(self, host, username, password, database, dbms = "mysql", driver = "SQL Server"):
        """
        This function sets the required url
        """
        try:
            if dbms == "mysql":
                self.url = f"mysql+pymysql://{username}:{password}@{host}:3306/{database}"
                self.engine = create_engine(self.url, pool_pre_ping=True)
                self.conn = self.engine.connect()
            elif dbms == "mssql":
                cnx_str = f'DRIVER={driver};SERVER={host};DATABASE={database};UID={username};PWD={password}'
                self.url = URL.create("mssql+pyodbc", query={"odbc_connect": cnx_str})
                self.engine = create_engine(self.url, pool_pre_ping=True)
                self.conn = self.engine.connect()
        except Exception as e:
            raise Exception(f"(__init__): Something went wrong on initiation process\n" + str(e))

    def closeConnection(self):
        try:
            self.conn.close()
        except Exception as e:
            raise Exception("(closeConnection): Something went wrong while closing the db connection\n" + str(e))

    def getDataFramebyQuery(self, query):
        """
        This function gets the query as input variable and returns the dataframe
        """
        try:
            df = pd.read_sql_query(query, self.engine)
            return df
        except Exception as e:
            raise Exception("(getDataFramebyQuery): Something went wrong while getting the dataframe object\n" + str(e))
    def insertSingleRecord(self, query, variables):
        try:
            self.cursor.execute(query, variables)
            self.conn.commit()
        except Exception as e:
            raise Exception("(insertSingleRecord): Could not insert the values in the database\n" + str(e))

    def executeOperation(self, query):
        try:
            self.engine.execute(query)
        except Exception as e:
            raise Exception("(executeOperation): Could not perform the DB operation\n" + str(e))
    def saveDataFrameIntoDB(self, df , name, index=False, if_exists='append'):
        try:
            df.to_sql(name=name, con=self.engine, index=index, if_exists=if_exists)
        except Exception as e:
            raise Exception("(saveDataFrameIntoDB): Could not upload the data to the database\n" + str(e))

   
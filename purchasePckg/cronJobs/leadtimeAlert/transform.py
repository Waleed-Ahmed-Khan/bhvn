import pandas as pd 
from utils import get_qty_done
import numpy as np

class DataOps:
    def __init__(self,sales_df, purchase_df):
        self.sales_df = sales_df
        self.purchase_df = purchase_df
        print(self.sales_df.columns.tolist())
        print(self.sales_df.shape, self.purchase_df.shape) 
        self.customer_po = self.sales_df["ponumber"].unique()[0]
        self.customer = self.sales_df["CustomerName"].unique()[0]
        self.mastercode = self.sales_df["mastercode"].unique()[0]


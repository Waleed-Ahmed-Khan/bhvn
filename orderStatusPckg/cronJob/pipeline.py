from extract import LoaderOLTP
from transform import DataOps

class Pipeline:
    def __init__(self, customer_po):
        self.customer_po = customer_po
        self.loader_oltp = LoaderOLTP(self.customer_po)
        
    def extract(self):
        self.purchase_order_qty, self.purchase_rcv, self.purchaseStart, self.purchaseEnd = self.loader_oltp.get_base_df_for_status('Purchase')
        self.cutting_df = self.loader_oltp.get_base_df_for_status('CT')
        self.auto_df = self.loader_oltp.get_base_df_for_status('AT')
        self.printing_df = self.loader_oltp.get_base_df_for_status('PT')
        self.issuance_df = self.loader_oltp.get_base_df_for_status('STI')
        self.sewing_df = self.loader_oltp.get_base_df_for_status('RFS')
        self.packing_df = self.loader_oltp.get_base_df_for_status('RFP')
        self.inspection_df = self.loader_oltp.get_base_df_for_status('FIN')
        self.sales_df = self.loader_oltp.get_base_df_for_status('Sales')
        self.logistics_df = self.loader_oltp.get_base_df_for_status('Logistics')
        #print(self.logistics_df)
        #print(self.cutting_df, self.auto_df, self.printing_df, self.issuance_df, self.sewing_df, self.packing_df, self.inspection_df)
    
    def transform(self):
        self.data_prep = DataOps(self.sales_df, self.purchase_order_qty, self.purchase_rcv, self.purchaseStart, self.purchaseEnd,
                self.cutting_df,self.auto_df,self.printing_df,self.issuance_df,self.sewing_df,self.packing_df,self.inspection_df, self.logistics_df)

        self.data_prep.level_one_vars(self.sales_df, self.logistics_df)

        self.data_prep.dep_status()

        self.final_df = self.data_prep.get_final_df()
        print(self.final_df)

    def load(self, loader):
        loader.loadIntoDB(self.final_df, "mfgcycle")
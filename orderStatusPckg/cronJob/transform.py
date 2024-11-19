import pandas as pd 
from utils import get_qty_done
import numpy as np

class DataOps:
    def __init__(self,sales_df, purchase_order_qty, purchase_rcv, purchaseStart, purchaseEnd,
                cutting_df,auto_df,printing_df,issuance_df,sewing_df,packing_df,inspection_df, logistics_df):
        self.sales_df = sales_df
        print(self.sales_df.columns.tolist()) 
        self.customer_po = self.sales_df["ponumber"].unique()[0]
        self.customer = self.sales_df["CustomerName"].unique()[0]
        self.mastercode = self.sales_df["mastercode"].unique()[0]
        self.purchase_order_qty = purchase_order_qty
        self.purchase_rcv = purchase_rcv
        self.purchaseStart = purchaseStart
        self.purchaseEnd = purchaseEnd
        self.cutting_df = cutting_df
        self.auto_df = auto_df
        self.printing_df = printing_df
        self.issuance_df = issuance_df
        self.sewing_df = sewing_df
        self.inspection_df = inspection_df 
        self.packing_df = packing_df
        self.logistics_df = logistics_df
        

    def get_min_max_leadtime(self, df):
        df.dropna(subset = ['date'], inplace = True)
        if len(df['date'].tolist())>0:
            min_date = df['date'].min()
            max_date = df['date'].max()
            leadtime = max_date - min_date
        else:
            min_date = np.nan
            max_date = np.nan
            leadtime = 0
        try:
            leadtime = leadtime.days
        except AttributeError:
            leadtime = 0
        return min_date, max_date, leadtime

    def dep_wise_status (self, dep_df, sales_df, item_part_wise = False, sizewise = False, item_partwise_for_cutting = False):
        sales_df = sales_df[['SalesOrder', 'ProductionNo','ponumber','itemid', 'description','size', 'CustomerName','itemqtyorder','cancel', 'confirm', 'confirmdate',
                            'duedate', 'ex_bhvn_date', 'bhvnorderentrydate', 'orderdate']].astype({'itemid':str})
        if item_part_wise:
            dep_df = dep_df.groupby(by=["itemid"], sort=False)['qty'].min().reset_index().astype({'itemid':str, 'qty':int})
            dep_order_status = pd.merge(sales_df, dep_df, how='left', on='itemid')
            return dep_order_status
        elif item_partwise_for_cutting:
            dep_df = dep_df.groupby(by=["itemid", "partid"]).sum().reset_index().astype({'qty':int})
            dep_df = dep_df.drop_duplicates(subset=['itemid'], keep='first')
            dep_order_status = pd.merge(sales_df, dep_df, how='left', on='itemid')
            return dep_order_status

        elif sizewise:
            dep_df = dep_df.groupby(by = ["size", "itemid"]).sum().reset_index()
            dep_df['itemid'] = dep_df['itemid'].apply(lambda x : x[:-3])
            dep_df = dep_df.drop_duplicates(subset=["size"], keep='first')
            dep_order_status = pd.merge(sales_df, dep_df, how='left', on='size')
            return dep_order_status
        else:
            dep_df = dep_df.groupby(by='itemid', as_index=True).sum()['qty'].reset_index().astype({'itemid':str, 'qty':int})
            dep_order_status = pd.merge(sales_df, dep_df, how='left', on='itemid')
            return dep_order_status
    
    def level_one_vars(self, sales_df, logistics_df):
        self.max_date_sales = sales_df['ex_bhvn_date'].unique()[0]
        self.min_date_sales = sales_df['orderdate'].unique()[0]

        self.inquiry_date = sales_df['inquirydate'].unique()[0]

        self.target_lead_time = self.max_date_sales - self.min_date_sales
        try:
            self.target_lead_time = self.target_lead_time.days
        except AttributeError:
            self.target_lead_time = 0

        try:
            self.sales_lead_time = self.min_date_sales - self.inquiry_date
        except TypeError:
            self.sales_lead_time = 0
        try:
            self.sales_lead_time = self.sales_lead_time.days
        except AttributeError:
            self.sales_lead_time = 0
    
        try:
            self.purchase_leadtime = self.purchaseEnd - self.purchaseStart
            self.purchase_leadtime = self.purchase_leadtime.days
        except TypeError:
            self.purchase_leadtime = 0
        except AttributeError:
            print("!!! Unexpected Behavior while calulating purchase lead time")
            self.purchase_leadtime = 0
        except:
            self.purchase_leadtime = 0 

        self.min_date_cutting , self.max_date_cutting , self.cutting_leadtime = self.get_min_max_leadtime(self.cutting_df) 
        self.min_date_auto , self.max_date_auto , self.auto_leadtime = self.get_min_max_leadtime(self.auto_df)
        self.min_date_printing , self.max_date_printing , self.printing_leadtime = self.get_min_max_leadtime(self.printing_df)
        self.min_date_issuance , self.max_date_issuance , self.issuance_leadtime = self.get_min_max_leadtime(self.issuance_df)
        self.min_date_sewing , self.max_date_sewing , self.sewing_leadtime = self.get_min_max_leadtime(self.sewing_df)
        self.min_date_fin , self.max_date_fin , self.fin_leadtime = self.get_min_max_leadtime(self.inspection_df)
        self.min_date_packing , self.max_date_packing , self.packing_leadtime = self.get_min_max_leadtime(self.packing_df)
        

        self.max_date_log = logistics_df['shipdate'].dropna().max()
        #min_date_log = log_df['booking_pdate'].dropna().min()
        try:
            if pd.notnull(self.max_date_sewing) and pd.notnull(self.max_date_log):
                self.min_date_log = self.max_date_sewing
                self.log_lead_time = self.max_date_log - self.min_date_log
            else:
                self.min_date_log = logistics_df['booking_pdate'].dropna().min()
                self.log_lead_time = self.max_date_log - self.min_date_log
            
            self.log_lead_time = self.log_lead_time.days
        except AttributeError:
            self.log_lead_time = 0

    def dep_status(self):
        try:
            try:
                self.cutting_status = self.dep_wise_status(self.cutting_df, self.sales_df, item_partwise_for_cutting=True)
            except KeyError:
                print("There is no data available for cutting")
                self.cutting_status = 0
            except Exception as e:
                print("Some unusual behavior is observered while getting the Cutting Department Status")
                self.cutting_status = 0
                raise e
            finally:
                pass
            try:
                self.printing_status = self.dep_wise_status(self.printing_df, self.sales_df, item_part_wise = False, sizewise=True) 
            except KeyError:
                print("There is no data available for Printing")
                self.printing_status = 0
            except:
                print("Some unusual behavior is observered while getting the Printing Department Status")
                self.printing_status = 0
            finally:
                pass

            try:
                self.auto_status = self.dep_wise_status(self.auto_df, self.sales_df, item_part_wise = False)
            except KeyError:
                print("There is no data available for Automation")
                self.auto_status = 0
            except:
                print("Some unusual behavior is observered while getting the Automation Department Status")
                self.auto_status = 0
            finally:
                pass

            try:
                self.issuance_status = self.dep_wise_status(self.issuance_df, self.sales_df)
            except KeyError:
                print("There is no data available for Issuance")
                self.issuance_status = 0
            except :
                print("Some unusual behavior is observered while getting the Issuance Status")
                self.issuance_status = 0
            finally:
                pass

            try:
                self.sewing_status = self.dep_wise_status(self.sewing_df, self.sales_df)
            except KeyError:
                print("There is no data available for Sewing")
                self.sewing_status = 0
            except :
                print("Some unusual behavior is observered while getting the Sewing Department Status")
                self.sewing_status = 0
            finally:
                pass

            try:
                self.fin_status = self.dep_wise_status(self.inspection_df, self.sales_df)
            except KeyError:
                print("There is no data available for Final Inspection")
                self.fin_status = 0
            except :
                print("Some unusual behavior is observered while getting the Final Inspection Status")
                self.fin_status = 0
            finally:
                pass


            try:
                self.packing_status = self.dep_wise_status(self.packing_df, self.sales_df)
            except KeyError:
                print("There is no data available for Packing")
                self.packing_status = 0
            except :
                print("Some unusual behavior is observered while getting the Packing Department Status")
                self.packing_status = 0
            finally:
                pass

            try:
                self.log_status = self.dep_wise_status(self.logistics_df, self.sales_df)
            except KeyError:
                print("There is no data available for Logistics")
                self.log_status = 0
            except Exception as e:
                #raise e 
                print("Some unusual behavior is observered while getting the Logistics Department Status")
                self.log_status = 0
            finally:
                pass

        except Exception as e:
            raise e
    
    def get_final_df(self):
        try:
            purchase_pct_complete = round(( self.purchase_rcv/self.purchase_order_qty)*100,0)
        except ZeroDivisionError:
            purchase_pct_complete = 0
        except TypeError:
            purchase_pct_complete = 0
        
        self.total_order_qty = self.sales_df['itemqtyorder'].sum()

        cutting_done, cutting_pct_complete = get_qty_done(self.cutting_status, self.total_order_qty)
        printing_done, printing_pct_complete = get_qty_done(self.printing_status, self.total_order_qty) 
        auto_done, auto_pct_complete = get_qty_done(self.auto_status, self.total_order_qty) 
        issuance_done, issuance_pct_complete = get_qty_done(self.issuance_status, self.total_order_qty)
        sewing_done, sewing_pct_complete = get_qty_done(self.sewing_status, self.total_order_qty)
        fin_done, fin_pct_complete = get_qty_done(self.fin_status, self.total_order_qty)
        packing_done, packing_pct_complete = get_qty_done(self.packing_status, self.total_order_qty)
        log_done, log_pct_complete = get_qty_done(self.log_status, self.total_order_qty)
       
        total_produced = log_done
        total_pct_complete = round((total_produced/self.total_order_qty)*100, 1)
        sewing_wip = issuance_done - sewing_done
        print(self.min_date_sales, self.max_date_sales, self.target_lead_time, self.sales_lead_time)
        final_df = pd.DataFrame([
            dict(CustomerPO=self.customer_po, Customer = self.customer, MasterCode = self.mastercode, Department="Target", Start=self.min_date_sales, Finish=self.max_date_sales, Completion_pct=total_pct_complete, LeadTime=str(self.target_lead_time), OrderQty = self.total_order_qty, OutputQty = log_done),
            dict(CustomerPO=self.customer_po, Customer = self.customer, MasterCode = self.mastercode, Department="Sales", Start=self.inquiry_date, Finish=self.min_date_sales, Completion_pct=100, LeadTime=str(self.sales_lead_time), OrderQty = self.total_order_qty, OutputQty = self.total_order_qty),
            dict(CustomerPO=self.customer_po, Customer = self.customer, MasterCode = self.mastercode, Department="Purchase", Start=self.purchaseStart, Finish=self.purchaseEnd, Completion_pct=purchase_pct_complete, LeadTime=str(self.purchase_leadtime), OrderQty = self.purchase_order_qty, OutputQty = self.purchase_rcv),
            dict(CustomerPO=self.customer_po, Customer = self.customer, MasterCode = self.mastercode, Department="Cutting", Start=self.min_date_cutting, Finish=self.max_date_cutting, Completion_pct=cutting_pct_complete, LeadTime=str(self.cutting_leadtime), OrderQty = self.total_order_qty, OutputQty = cutting_done),
            dict(CustomerPO=self.customer_po, Customer = self.customer, MasterCode = self.mastercode, Department="Printing", Start=self.min_date_printing, Finish=self.max_date_printing, Completion_pct=printing_pct_complete, LeadTime=str(self.printing_leadtime), OrderQty = self.total_order_qty, OutputQty = printing_done),
            dict(CustomerPO=self.customer_po, Customer = self.customer, MasterCode = self.mastercode, Department="Automation", Start=self.min_date_auto, Finish=self.max_date_auto, Completion_pct=auto_pct_complete, LeadTime=str(self.auto_leadtime), OrderQty = self.total_order_qty, OutputQty = auto_done),
            dict(CustomerPO=self.customer_po, Customer = self.customer, MasterCode = self.mastercode, Department="Issuance", Start=self.min_date_issuance, Finish=self.max_date_issuance, Completion_pct=issuance_pct_complete, LeadTime=str(self.issuance_leadtime), OrderQty = self.total_order_qty, OutputQty = issuance_done),
            dict(CustomerPO=self.customer_po, Customer = self.customer, MasterCode = self.mastercode, Department="Sewing", Start=self.min_date_sewing, Finish=self.max_date_sewing, Completion_pct=sewing_pct_complete, LeadTime=str(self.sewing_leadtime), OrderQty = self.total_order_qty, OutputQty = sewing_done),
            dict(CustomerPO=self.customer_po, Customer = self.customer, MasterCode = self.mastercode, Department="Final Inspection", Start=self.min_date_fin, Finish=self.max_date_fin, Completion_pct=fin_pct_complete, LeadTime=str(self.fin_leadtime), OrderQty = self.total_order_qty, OutputQty = fin_done),
            dict(CustomerPO=self.customer_po, Customer = self.customer, MasterCode = self.mastercode, Department="Packing", Start=self.min_date_packing, Finish=self.max_date_packing, Completion_pct=packing_pct_complete, LeadTime=str(self.packing_leadtime), OrderQty = self.total_order_qty, OutputQty = packing_done),
            dict(CustomerPO=self.customer_po, Customer = self.customer, MasterCode = self.mastercode, Department="Logistics", Start=self.min_date_log, Finish=self.max_date_log, Completion_pct=log_pct_complete, LeadTime=str(self.log_lead_time), OrderQty = self.total_order_qty, OutputQty = log_done)

        ]) 
        final_df['Finish'] = np.where(final_df['Start'], final_df['Finish'], None)
        return final_df
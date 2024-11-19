import pandas as pd 
from common import helper
import streamlit as st
from datetime import datetime, timedelta 
from st_aggrid import AgGrid

@st.cache(suppress_st_warning=True, show_spinner =False, ttl = 500000000000)
def get_base_df_for_status (dep_code, customer_po):
    if dep_code in ['RFS', 'FIN','RFP', 'STI', 'CT']:
        print(dep_code)
        query = f'''
        SELECT p.date, p.orderno AS "sale_order", p.ponumber AS "customer_PO", 
        p.ProductionNo AS "production_order", p.section, p.deptid, sec.name as "opr_code", 
        p_det.itemid, p_det.partid, tblitems.description,tblitems.size,
        working_hours, overtime_hours, tbl_itempart.description AS "Part", p_det.qty
        FROM bhvnerp_bhv2019.tblproduction_detail p_det
        left join bhvnerp_bhv2019.tblproduction p on p_det.entryno = p.entryno
        left join tbl_section sec on p.section = sec.id
        left join tbl_itempart on p_det.partid = tbl_itempart.id
        left join tblitems on p_det.itemid = tblitems.itemid
        where (p_det.entryno like'%{dep_code}%') and p.ponumber="{customer_po}";
        '''
        return helper.load_data(query)
    elif dep_code in ['PT']:
        query = f'''
                SELECT p.date, p.orderno AS "sale_order", p.ponumber AS "customer_PO", 
                p.ProductionNo AS "production_order", p.section, p.deptid, sec.name as "opr_code", 
                p_det.itemid, p_det.partid, tblitems.description,tblitems.size,
                working_hours, overtime_hours, tbl_itempart.description AS "Part", p_det.qty
                FROM bhvnerp_bhv2019.tblproduction_detail p_det
                left join bhvnerp_bhv2019.tblproduction p on p_det.entryno = p.entryno
                left join tbl_section sec on p.section = sec.id
                left join tbl_itempart on p_det.partid = tbl_itempart.id
                left join tblitems on p.order_itemid = tblitems.itemid
                where (p_det.entryno like'%{dep_code}%') and p.ponumber="{customer_po}"

        '''
        return helper.load_data(query)

    elif dep_code == 'Purchase':
        query_order_qty = f'''
        SELECT SUM(d.itemqty) AS ordqty FROM tblinvpodetail d , tblinvpo p 
        WHERE p.cust_ordno="{customer_po}" AND p.ponumber=d.ponumber;
        '''
        purchase_qty = f'''
                    SELECT 
                    SUM(md.qty_accepted) AS rcvqty, MIN(po.entrydate) AS purchaseStart, MAX(m.mirdate) purchaseEnd
                    FROM
                    tblmaterialinsepection m 
                    LEFT JOIN tblmaterialinspection_det md ON m.rcvid=md.rcvid
                    LEFT JOIN tblinvpo po ON m.ponumber = po.ponumber
                    WHERE 
                    m.ponumber 
                    IN
                    (SELECT ponumber FROM tblinvpo WHERE cust_ordno ="{customer_po}" )
        '''
        purchase_order_qty = helper.load_data(query_order_qty)
        purchase_order_qty = purchase_order_qty["ordqty"][0]
        purchase_qty = helper.load_data(purchase_qty)
        purchase_rcv = purchase_qty['rcvqty'][0]
        purchaseStart = purchase_qty['purchaseStart'][0]
        purchaseEnd = purchase_qty['purchaseEnd'][0]
        return purchase_order_qty, purchase_rcv, purchaseStart, purchaseEnd
    else :
        query = f'''
        SELECT p.date, p.orderno AS "sale_order", p.ponumber AS "customer_PO", 
        p.ProductionNo AS "production_order", p.section, p.deptid, sec.name as "opr_code", 
        p.order_itemid AS itemid, p_det.partid, tblitems.description,tblitems.size,
        working_hours, overtime_hours, tbl_itempart.description AS "Part", p_det.qty
        FROM bhvnerp_bhv2019.tblproduction_detail p_det
        left join bhvnerp_bhv2019.tblproduction p on p_det.entryno = p.entryno
        left join tbl_section sec on p.section = sec.id
        left join tbl_itempart on p_det.partid = tbl_itempart.id
        left join tblitems on p.order_itemid = tblitems.itemid
        where (p_det.entryno like'%{dep_code}%') and p.ponumber="{customer_po}";
        '''
        return helper.load_data(query)

    #left join ItemsTable on p_det.itemid = ItemsTable.itemid
@st.cache(suppress_st_warning=True, show_spinner =False, ttl = 500000000000)
def get_log_df(customer_po):
    query = f"""
    SELECT det.customer_ponumber,inv.bhvnpo, inv.custumInvoiceNo, det.invoiceid, inv.invoicedate, inv.shipdate,
        inv.booking_pdate,inv.booking_rdate, inv.shipcost,inv.AdvancePayment, inv.freight,
        inv.cosignee, inv.cosig_address, inv.brand, inv.bankname, inv.container, 
        inv.vesseldate, inv.vesselno, det.itemid, det.itemdescription, det.priceach, det.qty, 
        det.amount, det.discountPercent, det.exchange_rate, det.price_InCurrency,det.lotnumber, det.Cartons, 
        det.modelcode, det.hscode, det.imancode, det.container
    FROM tblinvoice inv
    LEFT JOIN tblinvoicedetail det ON
        det.invoiceid = inv.invoicenumber
    WHERE customer_ponumber="{customer_po}";
    """
    return helper.load_data(query)

@st.cache(suppress_st_warning=True, show_spinner =False, ttl = 500000000000)
def get_sales_df(customer_po):
    query = f'''
    SELECT tblarorderdetail.description, tblarorderdetail.itemid, tblitems.size, linenumber, orderid, itemqtyorder,
    saleunit, itempriceach, itemnote, lotnumber, tblarorder.id AS SalesOrder, tblarorder.ProductionNo, tblarorder.cancel, tblarorder.confirm, 
    tblarorder.confirmdate, tblcustomers.name AS CustomerName, tblarorder.duedate,tblarorder.ex_bhvn_date, tblarorder.bhvnorderentrydate, 
    tblarorder.orderdate, tblarorder.ponumber, tblarorder.shipTo_comp_name, tblarorder.shipTo_address 
    FROM tblarorderdetail 
    LEFT JOIN  tblarorder ON tblarorder.id = tblarorderdetail.orderid 
    LEFT JOIN tblcustomers ON tblcustomers.customerid = customer_id
    LEFT JOIN tblitems ON tblitems.itemid = tblarorderdetail.itemid
    WHERE ponumber="{customer_po}";
    '''
    return helper.load_data(query)

def dep_wise_status (dep_df, sales_df, item_part_wise = False, sizewise = False, item_partwise_for_cutting = False):
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
# def dep_wise_status (dep_df, sales_df):
#     sales_df = sales_df[['SalesOrder', 'ProductionNo','ponumber','itemid', 'description','size', 'CustomerName','itemqtyorder','cancel', 'confirm', 'confirmdate',
#                          'duedate', 'ex_bhvn_date', 'bhvnorderentrydate', 'orderdate']].astype({'itemid':str})
#     try:
#         try:
#             dep_df = dep_df.groupby(by='itemid', as_index=True).sum()['qty'].reset_index()
#         except KeyError:
#             dep_df = dep_df.groupby(by=["itemid"], sort=False)['qty'].min().reset_index()
#         dep_order_status = pd.merge(sales_df, dep_df, how='left', on='itemid')
#     except:
#         st.error('Yikes! Could not join Sales ans Manufacturing, Please Contact Admin ')
#     return dep_order_status

def get_status_vars(customer_po, item_description):
    purchase_order_qty, purchase_rcv, purchaseStart, purchaseEnd = get_base_df_for_status('Purchase', customer_po)
    cutting_df = get_base_df_for_status('CT', customer_po)
    auto_df = get_base_df_for_status('AT', customer_po)
    printing_df = get_base_df_for_status('PT', customer_po)
    issuance_df = get_base_df_for_status('STI', customer_po)
    sewing_df = get_base_df_for_status('RFS', customer_po)
    packing_df = get_base_df_for_status('RFP', customer_po)
    inspection_df = get_base_df_for_status('FIN', customer_po)

    sales_df = get_sales_df(customer_po)
    mask = sales_df['description'].isin(item_description)
    sales_df = sales_df.loc[mask]
    log_df = get_log_df(customer_po)
    try:
        max_date_sales = sales_df['duedate'].unique()[0]
        min_date_sales = sales_df['orderdate'].unique()[0]
        sales_lead_time = max_date_sales - min_date_sales
        try:
            sales_lead_time = sales_lead_time.days
        except AttributeError:
            sales_lead_time = 0
    
        
        try:
            #min_date_purchase = purchase_df.dropna(subset=['Order Date'])['Order Date'].min()
            #max_date_purchase = purchase_df.dropna(subset=['Received Date'])['Received Date'].max()
            
            purchase_leadtime = purchaseEnd - purchaseStart
        except TypeError:
            purchase_leadtime = 0
        except:
            #st.warning("An unusual behavior is observered while getting the purchase lead time, please contact admin")
            purchase_leadtime = 0
        
        try:
            purchase_leadtime = purchase_leadtime.days
        except AttributeError:
            purchase_leadtime = 0    
        

        min_date_issuance = issuance_df['date'].min()
        max_date_issuance = issuance_df['date'].max()
        issuance_leadtime = max_date_issuance - min_date_issuance
        try:
            issuance_leadtime = issuance_leadtime.days
        except AttributeError:
            issuance_leadtime = 0

        min_date_sewing = sewing_df['date'].min()
        max_date_sewing = sewing_df['date'].max()
        sewing_leadtime = max_date_sewing - min_date_sewing
        try:
            sewing_leadtime = sewing_leadtime.days
        except AttributeError:
            sewing_leadtime = 0
        min_date_cutting = cutting_df['date'].min()
        max_date_cutting = cutting_df['date'].max()
        cutting_leadtime = max_date_cutting - min_date_cutting
        try:
            cutting_leadtime = cutting_leadtime.days
        except AttributeError:
            cutting_leadtime = 0
        min_date_auto = auto_df['date'].min()
        max_date_auto = auto_df['date'].max()
        auto_leadtime = max_date_auto - min_date_auto
        try:
            auto_leadtime = auto_leadtime.days
        except AttributeError:
            auto_leadtime = 0
        min_date_printing = printing_df['date'].min()
        max_date_printing = printing_df['date'].max()
        printing_leadtime = max_date_printing - min_date_printing
        try:
            printing_leadtime = printing_leadtime.days
        except AttributeError:
            printing_leadtime = 0
                
        min_date_fin = inspection_df['date'].min()
        max_date_fin = inspection_df['date'].max()
        fin_leadtime = max_date_fin - min_date_fin
        try:
            fin_leadtime = fin_leadtime.days
        except AttributeError:
            fin_leadtime = 0
        
        min_date_packing = packing_df['date'].min()
        max_date_packing = packing_df['date'].max()
        packing_leadtime = max_date_packing - min_date_packing
        try:
            packing_leadtime = packing_leadtime.days
        except AttributeError:
            packing_leadtime = 0

        max_date_log = log_df['shipdate'].dropna().max()
        #min_date_log = log_df['booking_pdate'].dropna().min()
        try:
            if pd.notnull(max_date_sewing) and pd.notnull(max_date_log):
                min_date_log = max_date_sewing
                log_lead_time = max_date_log - min_date_log
            else:
                min_date_log = log_df['booking_pdate'].dropna().min()
                log_lead_time = max_date_log - min_date_log
            
            log_lead_time = log_lead_time.days
        except AttributeError:
            log_lead_time = 0

    except Exception as e: 
        raise e
    
    try:
        '''
        try:
            purchase_status = purchase_df.groupby(by=["Customer PO"], sort=False)['Received Qty', 'Ordered Qty'].mean().reset_index().astype({'Received Qty':int, 'Ordered Qty':int})  
        except KeyError:
            st.info("There is no data available for Purchase")
            purchase_status = 0
        except:
            #st.warning("Some unusual behavior is observered while getting the Purchase Status")
            purchase_status = 0
        finally:
            pass
        '''
    

        try:
            cutting_status = dep_wise_status(cutting_df, sales_df, item_partwise_for_cutting=True)
        except KeyError:
            st.info("There is no data available for cutting")
            cutting_status = 0
        except :
            st.warning("Some unusual behavior is observered while getting the Cutting Department Status")
            cutting_status = 0
        finally:
            pass
        try:
            printing_status = dep_wise_status(printing_df, sales_df, item_part_wise = False, sizewise=True) 
        except KeyError:
            st.info("There is no data available for Printing")
            printing_status = 0
        except:
            st.warning("Some unusual behavior is observered while getting the Printing Department Status")
            printing_status = 0
        finally:
            pass

        try:
            auto_status = dep_wise_status(auto_df, sales_df, item_part_wise = False)
        except KeyError:
            st.info("There is no data available for Automation")
            auto_status = 0
        except:
            st.warning("Some unusual behavior is observered while getting the Automation Department Status")
            auto_status = 0
        finally:
            pass

        try:
            issuance_status = dep_wise_status(issuance_df, sales_df)
        except KeyError:
            st.info("There is no data available for Issuance")
            issuance_status = 0
        except :
            st.warning("Some unusual behavior is observered while getting the Issuance Status")
            issuance_status = 0
        finally:
            pass

        try:
            sewing_status = dep_wise_status(sewing_df, sales_df)
        except KeyError:
            st.info("There is no data available for Sewing")
            sewing_status = 0
        except :
            st.warning("Some unusual behavior is observered while getting the Sewing Department Status")
            sewing_status = 0
        finally:
            pass

        try:
            fin_status = dep_wise_status(inspection_df, sales_df)
        except KeyError:
            st.info("There is no data available for Final Inspection")
            fin_status = 0
        except :
            st.warning("Some unusual behavior is observered while getting the Final Inspection Status")
            fin_status = 0
        finally:
            pass


        try:
            packing_status = dep_wise_status(packing_df, sales_df)
        except KeyError:
            st.info("There is no data available for Packing")
            packing_status = 0
        except :
            st.warning("Some unusual behavior is observered while getting the Packing Department Status")
            packing_status = 0
        finally:
            pass

        try:
            log_status = dep_wise_status(log_df, sales_df)
        except KeyError:
            st.info("There is no data available for Logistics")
            log_status = 0
        except:
            st.warning("Some unusual behavior is observered while getting the Logistics Department Status")
            log_status = 0
        finally:
            pass

    except Exception as e:
        raise e

    return (purchaseStart, purchaseEnd, purchase_leadtime,min_date_sewing,max_date_sewing, sewing_leadtime, min_date_cutting, max_date_cutting, cutting_leadtime,
        min_date_auto, max_date_auto,auto_leadtime, min_date_printing, max_date_printing, printing_leadtime, min_date_issuance, max_date_issuance,
         issuance_leadtime,fin_leadtime,max_date_fin, min_date_fin, packing_leadtime, max_date_packing,min_date_packing, max_date_sales, min_date_sales, 
        sales_lead_time, cutting_status, printing_status, auto_status,issuance_status, sewing_status,fin_status, packing_status, sales_df, purchase_order_qty, purchase_rcv,
        max_date_log, min_date_log, log_lead_time, log_status)


def get_all_customer_pos():
    query = f'''
        SELECT ponumber AS PO, shipTo_comp_name AS Customer, orderdate AS Date
        FROM tblarorder ;
    '''
    return helper.load_data(query)

def get_so(po_number):
    query = f'''
    SELECT DISTINCT(id) 
    FROM tblarorder 
    WHERE ponumber="{po_number}"
    '''
    return helper.load_data(query)

def get_item(po_number):
    query = f'''
            SELECT DISTINCT(tblarorderdetail.description)
            FROM tblarorderdetail 
            LEFT JOIN  tblarorder ON tblarorder.id = tblarorderdetail.orderid 
            WHERE ponumber="{po_number}"
    '''
    return helper.load_data(query)
    
def get_qty_done(df_status, total_order_qty):
    import pandas as pd 
    if isinstance(df_status, pd.DataFrame):
        try:
            total_done =  df_status['qty'].sum()
        except KeyError:
            total_done = 0
        pct_complete = round((total_done/total_order_qty)*100, 2)
    else:
        total_done = 0
        pct_complete = 0
    return total_done, pct_complete

def get_status(df):
    if df['OutputQty'] >= df['OrderQty']:
        return "Closed"
    else:
        return "Open"

def get_customers(po_datetime_selection):
    query = f'''
        SELECT DISTINCT(shipTo_comp_name) AS Customer FROM tblarorder
        WHERE orderdate >= "{po_datetime_selection}"
        ;
    '''
    return helper.load_data(query)

def get_po_selection_date(po_time_selection):
    if po_time_selection == "Last Week POs":
        po_time_selection = datetime.today() - timedelta(days=7)
    elif po_time_selection == "Last One Month POs":
        po_time_selection = datetime.today() - timedelta(days=30)
    elif po_time_selection == "Last Six Month POs":
        po_time_selection = datetime.today() - timedelta(days=183)
    elif po_time_selection == "Last One Year POs":
        po_time_selection = datetime.today() - timedelta(days=365)
    elif po_time_selection == "All POs from beginning":
        po_time_selection = '2013-01-01'
    return po_time_selection
def get_dep_status_vars(df, purchase = False):
    if purchase:
        min_date = df['Order Date'].min()
        max_date = df['Received Date'].max()
    else:
        min_date = df['date'].min()
        max_date = df['date'].max()
    leadtime = max_date - min_date
    try:
        leadtime = leadtime.days
    except AttributeError:
        leadtime = 0
    return min_date.strftime('%d %b, %Y'), max_date.strftime('%d %b, %Y'), leadtime

@st.cache(suppress_st_warning=True, show_spinner =False, ttl = 500000000000)
def get_df_for_purchase_status(customer_po):
    query = f'''
            SELECT
            po.cust_ordno AS 'Customer PO',
            po.production_ordno AS 'BHVN PO',
            po.ponumber AS 'Purchase Order #',
            tblitems.description AS 'Item Description',
            po.entrydate AS 'Order Date',
            po.duedate AS 'Required Date',
            mit.mirdate AS 'Received Date',
            TO_DAYS(mit.mirdate) - TO_DAYS(po.duedate) AS 'Delay (Days)',
            po_det.itemid AS itemid,
            vnd.vendorname AS 'Vendor Name',
            vnd.country AS Country,
            po_det.itemqty AS 'Ordered Qty',
            mit_det.qtyrcv AS 'Received Qty',
            mit_det.qty_rejected AS 'Rejected Qty',
            po_det.price_InCurrency AS 'Total Price Of Order',
            po_det.itempriceach AS 'Unit Price',
            vnd.category AS Category,
            vnd.nature AS Nature,
            CASE
                WHEN TO_DAYS(mit.mirdate) - TO_DAYS(po.duedate) >= 0 THEN 'Delayed'
                WHEN TO_DAYS(mit.mirdate) - TO_DAYS(po.duedate) < 0 THEN 'Ontime'
            END AS 'Ontime/Delay'
            FROM
            ((((
            tblmaterialinspection_det mit_det
            LEFT JOIN tblmaterialinsepection mit ON (mit_det.rcvid = mit.rcvid))
            LEFT JOIN tblinvpo po ON (mit.ponumber = po.ponumber))
            LEFT JOIN tblvendors vnd ON (mit.vendorid = vnd.vendorid))
            LEFT JOIN tblinvpodetail po_det ON (mit_det.podetid = po_det.podetid))
            LEFT JOIN tblitems ON (mit_det.itemid = tblitems.itemid)
            WHERE
            mit.rcvid = mit_det.rcvid
            AND
            mit.ponumber 
            IN
            (SELECT ponumber FROM tblinvpo WHERE cust_ordno="{customer_po}");
    '''
    return helper.load_data(query)
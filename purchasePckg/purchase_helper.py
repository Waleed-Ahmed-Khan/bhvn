from common import helper
import streamlit as st


@st.cache(suppress_st_warning=True, show_spinner = False, allow_output_mutation=True, ttl = 2000)
def get_purchase_data():
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
            CASE
                WHEN vnd.nature='Minor' THEN 'Low Risk'
                WHEN vnd.nature='Major' THEN 'Medium Risk'
                WHEN vnd.nature='Critical' THEN 'Operation Block'
                WHEN vnd.nature='' THEN 'Medium Risk'
            END AS 'Nature',
            CASE
                WHEN TO_DAYS(mit.mirdate) - TO_DAYS(po.duedate) >= 0 THEN 'Delayed'
                WHEN TO_DAYS(mit.mirdate) - TO_DAYS(po.duedate) < 0 THEN 'Ontime'
            END AS 'Ontime/Delay',
            CASE
                WHEN TO_DAYS(mit.mirdate) - TO_DAYS(po.duedate) < 0 THEN 1
                ELSE 0
            END AS 'Ontime_Orders',
            CASE
                WHEN TO_DAYS(mit.mirdate) - TO_DAYS(po.duedate) >= 0 THEN 1
                ELSE 0
            END AS 'Delayed_Orders',
            CASE
                WHEN po.import=0 THEN 'Local'
                WHEN po.import=1 THEN 'Import'
            END AS 'source'
            FROM
            ((((
            tblmaterialinspection_det mit_det
            LEFT JOIN tblmaterialinsepection mit ON (mit_det.rcvid = mit.rcvid))
            LEFT JOIN tblinvpo po ON (mit.ponumber = po.ponumber))
            LEFT JOIN tblvendors vnd ON (mit.vendorid = vnd.vendorid))
            LEFT JOIN tblinvpodetail po_det ON (mit_det.podetid = po_det.podetid))
            LEFT JOIN tblitems ON (mit_det.itemid = tblitems.itemid)
            WHERE
            po.entrydate >= '2022-01-01'
            AND
            mit.rcvid = mit_det.rcvid
    '''
            #     AND
            # po.import=0
            # AND 
            # mit.import=0;
    return helper.load_data(query)
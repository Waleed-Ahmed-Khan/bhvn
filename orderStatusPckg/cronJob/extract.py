import os , sys
from pathlib import Path
FILE = Path(__file__).resolve()
ROOT = FILE.parents[2]  # root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative

from common import helper

class LoaderOLTP:
    def __init__(self, customer_po):
        self.customer_po = customer_po

    def get_base_df_for_status (self, dep_code):
        if dep_code in ['RFS', 'FIN','RFP', 'STI', 'CT']:
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
            where (p_det.entryno LIKE '%{dep_code}%') and p.ponumber="{self.customer_po}";
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
                    where (p_det.entryno like'%{dep_code}%') and p.ponumber="{self.customer_po}"

            '''
            return helper.load_data(query)

        elif dep_code == 'Purchase':
            query_order_qty = f'''
            SELECT SUM(d.itemqty) AS ordqty FROM tblinvpodetail d , tblinvpo p 
            WHERE p.cust_ordno="{self.customer_po}" AND p.ponumber=d.ponumber;
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
                        (SELECT ponumber FROM tblinvpo WHERE cust_ordno ="{self.customer_po}" )
            '''
            purchase_order_qty = helper.load_data(query_order_qty)
            purchase_order_qty = purchase_order_qty["ordqty"][0]
            purchase_qty = helper.load_data(purchase_qty)
            purchase_rcv = purchase_qty['rcvqty'][0]
            purchaseStart = purchase_qty['purchaseStart'][0]
            purchaseEnd = purchase_qty['purchaseEnd'][0]
            return purchase_order_qty, purchase_rcv, purchaseStart, purchaseEnd
        elif dep_code == 'Logistics':
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
            WHERE customer_ponumber="{self.customer_po}";
            """
            return helper.load_data(query)
        elif dep_code == "Sales":
            query = f'''
            SELECT tblarorderdetail.description, tblitems.mastercode, tblarorderdetail.itemid, tblitems.size, tblarorderdetail.orderid, tblarorderdetail.itemqtyorder,
            tblarorderdetail.saleunit, tblarorderdetail.itempriceach, tblarorderdetail.itemnote, tblarorderdetail.lotnumber, tblarorder.id AS SalesOrder, inquirydate, tblarorder.ProductionNo, tblarorder.cancel, tblarorder.confirm, 
            tblarorder.confirmdate, tblcustomers.name AS CustomerName, tblarorder.duedate,tblarorder.ex_bhvn_date, tblarorder.bhvnorderentrydate, 
            tblarorder.orderdate, tblarorder.ponumber, tblarorder.shipTo_comp_name, tblarorder.shipTo_address 
            FROM tblarorderdetail 
            LEFT JOIN  tblarorder ON tblarorder.id = tblarorderdetail.orderid 
            LEFT JOIN tblcustomers ON tblcustomers.customerid = customer_id
            LEFT JOIN tblitems ON tblitems.itemid = tblarorderdetail.itemid
            LEFT JOIN tblorder_inquiry ON tblorder_inquiry.id = tblarorder.inquiryorder
            WHERE tblarorder.ponumber="{self.customer_po}";
            '''
            return helper.load_data(query)
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
            where (p_det.entryno like'%{dep_code}%') and p.ponumber="{self.customer_po}";
            '''
            return helper.load_data(query)

        
import streamlit as st
import matplotlib.pyplot as plt
import static.formatHelper as fh
from purchasePckg.purchase_main import render_last_working_day, render_purchase_operations, render_vendor_analysis
from streamlit_option_menu import option_menu
from purchasePckg.purchase_helper import get_purchase_data
import numpy as np 
import pandas as pd
from st_aggrid import AgGrid
plt.style.use('fivethirtyeight')

def get_purchase_variables ():
    #query = "SELECT * FROM PurchaseView1"
    with st.spinner("Purchase Dashboard is getting ready for you ♾️"):
        purch = get_purchase_data()
    purch.drop_duplicates(keep='first', inplace=True)
    purch.dropna(subset=["Customer PO", "BHVN PO", "Purchase Order #"])
    purch1 = purch.copy()
    purch = purch.drop_duplicates(subset = ['Customer PO', 'BHVN PO', 'Purchase Order #', 'Item Description', 'Order Date', 'Required Date', 'Ordered Qty'], keep = "first")
    cols_to_groupby = ['Customer PO', 'BHVN PO', 'Purchase Order #', 'Item Description', 'Order Date', 'Required Date', 'source', 'Ordered Qty', 'Received Qty']
    #purch1 = pd.DataFrame()
    cols_to_groupby_without_receive_qty = ['Customer PO', 'BHVN PO', 'Purchase Order #', 'Item Description', 'Order Date', 'Required Date', 'source', 'Ordered Qty']
    purch1 = purch1[cols_to_groupby].groupby(cols_to_groupby_without_receive_qty).agg({"Received Qty":"sum"}).reset_index()
    purch = pd.merge(left= purch, right = purch1, how = 'left', on=cols_to_groupby_without_receive_qty)
    purch.drop(columns=['Received Qty_x'], inplace=True)
    purch.rename(columns={'Received Qty_y':'Received Qty'}, inplace=True)
    purch['Order Status'] = np.where(purch['Ordered Qty'] > purch['Received Qty'] ,"Open", "Closed")
    del(purch1)
    #pd.to_datetime(purch['Order Date'])
    #purch[['Order Date', 'Required Date', 'Received Date']] = purch[['Order Date', 'Required Date', 'Received Date']].astype('datetime64')
    #pd.to_datetime(purch[['Order Date', 'Required Date', 'Received Date']], format='%Y/%m/%d')
    #purch[['Customer PO1', 'BHVN PO1', 'Purchase Order #1', "Item Description1", "Order Date1", "Required Date1", "Ordered Qty1", "Received Qty1"]] = purch[['Customer PO', 'BHVN PO', 'Purchase Order #', 'Item Description', 'Order Date', 'Required Date', 'Ordered Qty', 'Received Qty']].shift(periods=1, axis = 0)
    #for index, row in purch.iterrows():
    #    if (row['Customer PO'], row['BHVN PO'], row['Purchase Order #'], row['Item Description'], row['Order Date'], row['Required Date'], row['Ordered Qty'] == row["Customer PO1"], row["BHVN PO1"], row["Purchase Order #1"], row["Item Description1"], row["Order Date1"], row["Required Date1"], row["Ordered Qty1"]):
    #        row['Received Qty'] += row['Received Qty1']
    purch_order_status = purch['Order Status'].unique().tolist()
    purchase_po_list = purch['Purchase Order #'].unique().tolist()
    purchase_po_list.insert(0, 'All POs')
    date = [pd.to_datetime(i).date() for i in purch['Order Date'].dropna().unique().tolist()]
    purch["year"] = purch['Order Date'].astype('datetime64').dt.year
    year = [int(i) for i in purch['year'].dropna().unique().tolist()]
    year.reverse()
    customer_po_list = purch['Customer PO'].unique().tolist()
    customer_po_list.insert(0, "All POs")
    vendor_list = purch['Vendor Name'].unique().tolist()
    vendor_list.insert(0, "All Vendors")
    categories_list = purch['Category'].unique().tolist()
    #categories_list = purch[purch['Category']!= '']['Category'].unique().tolist()
    categories_list.insert(0, "All Categories")
    source = purch['source'].unique().tolist()
    #source.insert(0, "All Sources")
    purch = purch.drop_duplicates(keep='first')

    return purch, date, purchase_po_list, purch_order_status, year, customer_po_list, vendor_list, categories_list, source


def render_purchase(username):
    
    st.write('<style>div.row-widget.stButton > div{flex-direction:row;} </style>', unsafe_allow_html=True)
    st.write('<style>div.st-bf{flex-direction:column;} div.st-ag{font-weight:bold;padding-left:2px;}</style>', unsafe_allow_html=True)
    st.write(fh.format_st_button(), unsafe_allow_html=True)

    selection = option_menu(

                menu_title = "Purchase Department",
                options = ['Purchase Opertaions', 'Last Working Day', 'Vendor Analysis'],
                icons = ["wallet2", "alarm-fill", "pie-chart-fill"],
                menu_icon = ["receipt"],
                orientation = "horizontal"
    )

    try:
        if selection == 'Purchase Opertaions' :
            render_purchase_operations(username)

        elif selection == 'Last Working Day':
            render_last_working_day(username)
        
        elif selection == 'Vendor Analysis':
            render_vendor_analysis(username)
    except Exception as e:
        #st.error(f"Dear {str.title(username)}, Something went wrong. Please contact admin in case the problem persists. We are sorry 😌")
        raise (e)
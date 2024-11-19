
import streamlit as st
from common import helper, vizHelper
import adminPckg.userManagement as userManagement
import pandas as pd
import static.formatHelper as fh
from st_aggrid import AgGrid
from salesPckg import sales_helper
from static.formatHelper import hover_size
from vizpool.interactive import EDA

def get_sales_vars_l():
    with st.spinner("Please stay with us while we get things ready for you... ⏳"):
        sales_df = sales_helper.get_sales_data_l()
        date = sales_df['Sales Month'].unique().tolist()
        customer_po_list = sales_df['Customer PO Number'].unique().tolist()
        customer_po_list.insert(0, 'All POs')   
        customer_list = sales_df['Customer'].unique().tolist()
        customer_list.insert(0, 'All Customers')
        brand_list = sales_df['Brand'].unique().tolist()
        brand_list.insert(0, 'All Brands')
        return sales_df, date, customer_po_list, customer_list, brand_list

def render_sales_operations_l(username):
    st.write(fh.format_st_button(), unsafe_allow_html=True)
    st.markdown(hover_size(), unsafe_allow_html=True)
    sales_df, date, customer_po_list, customer_list, brand_list = get_sales_vars_l()

    with st.form(key = "sales_form0"):
        col1, col2, col3, col4, col5 =  st.columns(5)
        with col1:
            st.markdown("**Start Date :**")
            start_date = st.date_input('', pd.to_datetime(min(date)))
        with col2:
            st.markdown("**End Date :**")
            end_date = st.date_input('', pd.to_datetime(max(date)))
        with col3:
            st.markdown("**Customer PO :**")
            po_selection = st.multiselect('',  customer_po_list, default='All POs')
        with col4:
            st.markdown("**Customer :**")
            customer_selection = st.multiselect('',  customer_list, default='All Customers')
        with col5:
            st.markdown("**Brand :**")
            brand_selection = st.multiselect('',  brand_list, default='All Brands')
        st.markdown('<hr/>', unsafe_allow_html = True)
        st.form_submit_button(label = '📈 Build Dashboard')
        
    if po_selection ==["All POs"]:
        po_selection = customer_po_list
    if customer_selection ==["All Customers"]:
        customer_selection = customer_list
    if brand_selection ==["All Brands"]:
        brand_selection = brand_list

    sales_df_t, monthly_data, customer_wise = sales_helper.data_processing_sales_l(sales_df, start_date, end_date, po_selection, customer_selection, brand_selection)
    if isinstance (sales_df_t, pd.DataFrame):
        try:
            kpi1, kpi2,kpi3 =  st.columns(3)
            with kpi1:
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>Delay CHD</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{int(sales_df_t['Delay CHD'].mean())} days</h4>", unsafe_allow_html= True)
                with st.expander("Delay CHD Formula"):
                    st.latex(r'''
                    =\left(\frac{Σ(AHD - CHD)}{Total Shipments}\right) *100
                    ''')
            with kpi2:
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>Delay EHD</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{int(sales_df_t['Delay EHD'].mean())} days</h4>", unsafe_allow_html= True)
                with st.expander("Delay EHD Formula"):
                    st.latex(r'''
                    =\left(\frac{Σ(AHD - EHD)}{Total Shipments}\right) *100
                    ''')
            with kpi3:
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>Avg Booking Confirmation Time</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{int(sales_df_t['Booking Confirmation Days'].mean())} days</h4>", unsafe_allow_html= True)
                with st.expander("Avg Booking Confirmation Time Formula"):
                    st.latex(r'''
                    =\left(\frac{Σ(Booking Confirmation Time)}{Total Bookings}\right)
                    ''')
            st.markdown('<hr/>', unsafe_allow_html = True)
            
            kpi1, kpi2,kpi3 =  st.columns(3)
            with kpi1:
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>HOT CHD</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{round(monthly_data['HOT_CHD'].mean()*100, 2)} %</h4>", unsafe_allow_html= True)
                with st.expander("HOT CHD Formula"):

                    #st.latex(r"$$Avg Eff = \frac{Σ Efficiency}{Σ Working Days}$$")
                    st.latex(r'''
                    =\left(\frac{Σ(Qty On TIME w.r.t CHD)}{Total Qty Shipped}\right) * 100
                    ''')
            with kpi2:
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>HOT EHD</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{round(monthly_data['HOT_EHD'].mean()*100, 2)} %</h4>", unsafe_allow_html= True)
                with st.expander("HOT EHD Formula"):
                    st.latex(r'''
                    =\left(\frac{Σ(Qty On TIME w.r.t EHD)}{Total Qty Shipped}\right)
                    ''')
            with kpi3:
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>Total Orders Shipped</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{(sales_df_t['Inv. Number'].nunique())}</h4>", unsafe_allow_html= True)
                with st.expander("Formula"):
                    st.latex(r'''
                    =Σ Sale Orders
                    ''')
            st.markdown('<hr/>', unsafe_allow_html = True)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>Total Qty Shipped</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{int(sales_df_t['Qty'].sum())} pairs</h4>", unsafe_allow_html= True)
            with col2:
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>Qty Delayed</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{int(monthly_data['QtyDelayedEHD'].sum())} pairs</h4>", unsafe_allow_html= True)
            with col3:
                st.markdown(f"<h5 style = 'text-align: center; color: red;'>Sales Value</h5>", unsafe_allow_html= True)
                st.markdown(f"<h4 style = 'text-align: center; color: blue;'>$ {int(sales_df_t['Total Value (US$)'].sum())}</h4>", unsafe_allow_html= True)

            st.markdown('<hr/>', unsafe_allow_html = True)

            
            col1, col2 = st.columns(2)
            
    
            col1.plotly_chart(vizHelper.multivar_areachart(monthly_data, 'SalesMonth', values = ['HOT_EHD_2021', 'HOT_EHD_2022'], legends = ['2021', '2022'], title = "Monthly HOT (EHD)", unit = "%"))
            #col2.plotly_chart(vizHelper.pie_chart(customer_qty, 'Quantity', 'Customer Name', title='Customer wise Production Ratio'))
            col2.plotly_chart(vizHelper.multivar_areachart(monthly_data, 'SalesMonth', values = ['HOT_CHD_2021', 'HOT_CHD_2022'], legends = ['2021', '2022'], title = "Monthly HOT (CHD)", unit = "%"))
            st.header("Sales Data")
            
            #sales_df_t = sales_df_t.drop(columns=["Unnamed: 0"])
            AgGrid(sales_df_t)
            df_xlsx = helper.to_excel(sales_df_t)
            st.download_button(label='📥 Download Dataset',
                                data=df_xlsx ,
                                file_name= 'SalesData.xlsx')
            userManagement.app_logger(username, "Sales Dashboard Legacy")
            
        except Exception as e:
            pass

def render_sales_form(username):
    with st.form(key='sales-form'):
        st.header('Add Sales Data')
        st.subheader('📤 Please Upload an Excel file')
        uploaded_data = st.file_uploader('')
        submit_sales_form = st.form_submit_button(label = '✔ Submit Data')
        
        if submit_sales_form:
            if uploaded_data is not None:
                try:
                    try:
                        with st.spinner("Please stay with us while we upload your data..."):
                            sales_helper.upload_sales(uploaded_data, username)
                    except Exception as e: 
                        raise e
                        #st.error(f"Oh {str.title(username)}, data could not be uploaded in the database because same data may already exist in the database or the provided file format is not correct. Please contact admin in case the problem persists. We are sorry 😌")
                except Exception as e:
                    raise e
                    st.error(f"Dear {str.title(username)}, file could not be uploaded properly. Please contact admin in case the problem persists. We are sorry 😌")
    
    with st.form(key='update_sales_form'):
        st.header("Update Sales Data")
        
        st.subheader('📤 Please Upload an Excel file')
        uploaded_data = st.file_uploader('')


        update_sales_data = st.form_submit_button(label = '📝Update Data')
        
        if update_sales_data:
            try:
                if uploaded_data is not None:
                    sales_helper.update_sales(uploaded_data, "bhvndb", "bhvnSales", username)
            except Exception as e:
                raise e
                #st.error(f"Sorry {str.title(username)}, we could not update the data. please contact admin in case the problem persists ")
def get_sales_vars(username):
    with st.spinner(f"Hey {str.title(username)}, Sales Dashboard is getting ready for you... ⏳"):
        sales_df = sales_helper.load_sales_invoice_data()
        date = sales_df['invoicedate'].unique().tolist()
        customer_po_list = sales_df['ponumber'].unique().tolist()
        customer_po_list.insert(0, 'All POs')   
        customer_list = sales_df['custname'].unique().tolist()
        customer_list.insert(0, 'All Customers')
        custum_inv_list = sales_df['custumInvoiceNo'].unique().tolist()
        custum_inv_list.insert(0, 'All Invoices')
        year = sales_df['year'].dropna().unique().tolist()
        return sales_df, date, customer_po_list, customer_list, custum_inv_list, year


def render_sales_opreations(username):
    st.write(fh.format_st_button(), unsafe_allow_html=True)
    st.markdown(hover_size(), unsafe_allow_html=True)
    sales_df, date, customer_po_list, customer_list, custum_inv_list, year = get_sales_vars(username)
    with st.form(key = "sales_form0"):
        col1, col2, col3, col4, col5, col6 =  st.columns(6)
        with col1:
            st.markdown("**Start Date :**")
            start_date = st.date_input('', (pd.to_datetime(date)).min())
        with col2:
            st.markdown("**End Date :**")
            end_date = st.date_input('', (pd.to_datetime(date)).max())
        with col3:
            st.markdown("**Customer PO :**")
            po_selection = st.multiselect('',  customer_po_list, default='All POs')
        with col4:
            st.markdown("**Customer :**")
            customer_selection = st.multiselect('',  customer_list, default='All Customers')
        with col5:
            st.markdown("**Invoice Number :**")
            inv_selection = st.multiselect('',  custum_inv_list, default='All Invoices')
        with col6:
            st.markdown("**Year :**")
            year = st.selectbox('', year)
        st.markdown('<hr/>', unsafe_allow_html = True)
        st.form_submit_button(label = '📈 Build Dashboard')
        
    if po_selection ==["All POs"]:
        po_selection = customer_po_list
    if customer_selection ==["All Customers"]:
        customer_selection = customer_list
    if inv_selection ==["All Invoices"]:
        inv_selection = custum_inv_list

    if isinstance (sales_df, pd.DataFrame):
        try:
            sales_df = sales_helper.preprocess_sales(sales_df, start_date, end_date, year, po_selection, customer_selection,inv_selection)
            kpi1, kpi2,kpi3 =  st.columns(3)
            with kpi1:
                st.markdown(f"<h4 style = 'text-align: center; color: red;'>Avg Target Lead time</h4>", unsafe_allow_html= True)
                st.markdown(f"<h5 style = 'text-align: center; color: blue;'>{int(sales_df['target_lead_time'].mean())} days</h5>", unsafe_allow_html= True)
                with st.expander("Avg Target Lead time Formula"):

                    #st.latex(r"$$Avg Eff = \frac{Σ Efficiency}{Σ Working Days}$$")
                    st.latex(r'''
                    =\left(\frac{Σ(Due Date - Order Date)}{Total Shipments}\right)
                    ''')
            with kpi2:
                st.markdown(f"<h4 style = 'text-align: center; color: red;'>Avg Actual Lead time</h4>", unsafe_allow_html= True)
                st.markdown(f"<h5 style = 'text-align: center; color: blue;'>{int(sales_df['actual_lead_time'].mean())} days</h5>", unsafe_allow_html= True)
                with st.expander("Avg Actual Lead time Formula"):

                    #st.latex(r"$$Avg Eff = \frac{Σ Efficiency}{Σ Working Days}$$")
                    st.latex(r'''
                    =\left(\frac{Σ(Shipment Date - Order Date)}{Total Shipments}\right)
                    ''')
            with kpi3:
                st.markdown(f"<h4 style = 'text-align: center; color: red;'>Avg Delay(Days)</h4>", unsafe_allow_html= True)
                st.markdown(f"<h5 style = 'text-align: center; color: blue;'>{int(sales_df['delay_days'].mean())} days</h5>", unsafe_allow_html= True)
                with st.expander("Avg Delay(Days) Formula"):
                    st.latex(r'''
                    =\left(\frac{Σ(Actual LT - Target LT)}{Total Bookings}\right)
                    ''')
            st.markdown('<hr/>', unsafe_allow_html = True)
            
            kpi1, kpi2,kpi3 =  st.columns(3)
            with kpi1:
                st.markdown(f"<h4 style = 'text-align: center; color: red;'>Avg Booking Confirmation days</h4>", unsafe_allow_html= True)
                st.markdown(f"<h5 style = 'text-align: center; color: blue;'>{int(sales_df['booking_conf_time'].mean())} days</h5>", unsafe_allow_html= True)
                with st.expander("Avg Booking Confirmation days"):
                    st.latex(r'''
                    =\left(\frac{Σ(Confirmation - Placement)}{Total Bookings}\right)
                    ''')
            with kpi2:
                st.markdown(f"<h4 style = 'text-align: center; color: red;'>Percent Qty Delayed</h4>", unsafe_allow_html= True)
                st.markdown(f"<h5 style = 'text-align: center; color: blue;'>{round(sales_df['percent_qty_delayed'].mean(), 0)} %</h5>", unsafe_allow_html= True)
                with st.expander("Percent Qty Delayed"):
                    st.latex(r'''
                    =\left(\frac{Σ(Delayed Qty)}{Total Qty Shipped}\right)*100
                    ''')
            with kpi3:
                st.markdown(f"<h4 style = 'text-align: center; color: red;'>Handover On-Time (HOT)</h4>", unsafe_allow_html= True)
                st.markdown(f"<h5 style = 'text-align: center; color: blue;'>{int(sales_df['HOT'].mean())} %</h5>", unsafe_allow_html= True)
                with st.expander("Handover On-Time Formula"):
                    st.latex(r'''
                    =\left(\frac{Σ(Qty Ontime)}{Total Qty Shipped}\right)*100
                    ''')
            st.markdown('<hr/>', unsafe_allow_html = True)

            col1, col2 = st.columns(2)
            sales_df.rename(columns={'salesmonth': 'Sales Month', 'shipped_qty':'Shipped Qty',
                                     'custname': 'Customer', 'target_lead_time': 'Target Lead-time',
                                     'actual_lead_time': 'Actual Lead-time', 'delay_days': 'Delay (Days)',
                                     'booking_conf_time':'Booking Confirmation Time', 'lotnumber_x': 'Lot Number'}, inplace = True)
            sales_instance = EDA(sales_df)
            col1.plotly_chart(sales_instance.area_chart(categories='Sales Month', values = 'Price(USD)', title = 'Monthly Sales Value', aggfunc = 'sum',
                                                        unit = "$", unit_position= 'before', sort_by = 'salesmonth_number'))
            col2.plotly_chart(sales_instance.area_chart(categories='Sales Month', values = 'Shipped Qty', unit = None, aggfunc='sum',
                                                                sort_by ='salesmonth_number', title = 'Monthly Sales Quantity'))

            col1, col2 = st.columns(2)
            col1.plotly_chart(sales_instance.piechart(categories='Customer', values = 'Price(USD)',  width = 450, height = 500,
                             title = "Customer wise Revenue Ratio"))
            col2.plotly_chart(sales_instance.piechart(categories='Customer', values = 'Shipped Qty',  width = 450, height = 500,
                             title = "Customer wise Order Qty Ratio"))   
            col1, col2 = st.columns(2)
            col1.plotly_chart(sales_instance.stack_or_group_chart(categories='Customer', values = ['Target Lead-time', 'Actual Lead-time'], unit = "days", orientation ='h',
                    sort_by ='Actual Lead-time', barmode = 'stack', title = 'Customer wise Target and Actual Lead Time'))                                           
            col2.plotly_chart(sales_instance.area_chart(categories='Sales Month', values = 'Delay (Days)', unit = "days", aggfunc='mean',
                                                    sort_by ='salesmonth_number', title = 'Month wise Avg Order Delay'))
            col1, col2 = st.columns(2)
            col1.plotly_chart(sales_instance.stack_or_group_chart(categories='Customer', values = ['HOT'], unit = "%", orientation ='h',
                    sort_by ='HOT', barmode = 'stack', title = 'Customer wise HOT(Handover On-time'))                                           
            col2.plotly_chart(sales_instance.area_chart(categories='Sales Month', values = 'HOT', unit = "%", aggfunc='mean',
                                                    sort_by ='salesmonth_number', title = 'Monthly HOT(Handover On-time)'))

            col1, col2 = st.columns(2)
            col1.plotly_chart(sales_instance.area_chart(categories='Sales Month', values = 'Booking Confirmation Time', unit = "days", aggfunc='mean',
                                                    sort_by ='salesmonth_number', title = 'Monthly Booking Confirmation Time'))
            col2.plotly_chart(sales_instance.combined_corr(x_values='Booking Confirmation Time',y_values = 'Delay (Days)',color='Customer',
                                size = 'Shipped Qty', hover_name='Customer'))
            sales_df.drop(['lotnumber_y', 'salesmonth_number', 'pomonth_number'], axis = 1, inplace = True)
            st.header("Sales Data")
            AgGrid(sales_df)
            df_xlsx = helper.to_excel(sales_df)
            st.download_button(label='📥 Download Dataset',
                                data=df_xlsx ,
                                file_name= 'SalesData.xlsx')

            #userManagement.app_logger(username, "Sales Operational Dashboard")
        except ValueError:
            st.error("PO does does not hold the valid data to be presented, please select another PO")

        except Exception as e:
            raise e
            st.error(f"Sorry {str.title(username)}, could not process your request at the momenet, please contact admin if the problem persists.😟") 

def render_sales_transaction(username):
    st.write(fh.format_st_button(), unsafe_allow_html=True)
    st.markdown(hover_size(), unsafe_allow_html=True)
    with st.spinner(f"Hey {str.title(username)}, Sales Dashboard is getting ready for you... ⏳"):
        sales_df = sales_helper.load_sales_invoice_data()
    inv_list = sales_df['custumInvoiceNo'].unique().tolist()
    customer_po_list = sales_df['ponumber'].unique().tolist()
    st.write('<style>div.row-widget.stRadio > div{flex-direction:row;} </style>', unsafe_allow_html=True)
    st.write('<style>div.st-bf{flex-direction:column;} div.st-ag{font-weight:bold;padding-left:2px;}</style>', unsafe_allow_html=True)
    filter_selection = st.radio("",('Filter By Invoice Number', 'Filter By Customer PO'))
    col1, col2 = st.columns(2)
    if filter_selection == "Filter By Customer PO":
        with col1:
            po_selection  = st.selectbox("", customer_po_list)
            sales_df = sales_df[sales_df['ponumber'] == po_selection]
    elif filter_selection == "Filter By Invoice Number":
        with col1:
            inv_selection  = st.selectbox("", inv_list)
            sales_df = sales_df[sales_df['custumInvoiceNo'] == inv_selection]

    if st.button("📈 Build Dashboard"):
        try:
            total_order_qty = int(sales_df['order_qty'].sum())
            total_shiped_qty = int(sales_df['shipped_qty'].sum())
            qty_balance = total_order_qty - total_shiped_qty

            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.markdown(f"<h4 style = 'text-align: center; color: red;'>Customer PO</h4>", unsafe_allow_html= True)
                st.markdown(f"<h5 style = 'text-align: center; color: blue;'>{sales_df['custponumber'].unique()}</h5>", unsafe_allow_html= True)
            with col2:
                st.markdown(f"<h4 style = 'text-align: center; color: red;'>Sales Order</h4>", unsafe_allow_html= True)
                st.markdown(f"<h5 style = 'text-align: center; color: blue;'>{sales_df['SalesOrder'].unique()}</h5>", unsafe_allow_html= True)
            with col3:
                st.markdown(f"<h4 style = 'text-align: center; color: red;'>BHVN PO</h4>", unsafe_allow_html= True)
                st.markdown(f"<h5 style = 'text-align: center; color: blue;'>{sales_df['ProductionNo'].unique()}</h5>", unsafe_allow_html= True)
            with col4:
                st.markdown(f"<h4 style = 'text-align: center; color: red;'>Target Lead time</h4>", unsafe_allow_html= True)
                st.markdown(f"<h5 style = 'text-align: center; color: blue;'>{int(sales_df['target_lead_time'].mean())} days</h5>", unsafe_allow_html= True)
            with col5:
                st.markdown(f"<h4 style = 'text-align: center; color: red;'>Actual Lead time</h4>", unsafe_allow_html= True)
                st.markdown(f"<h5 style = 'text-align: center; color: blue;'>{int(sales_df['actual_lead_time'].mean())} days</h5>", unsafe_allow_html= True)


            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.markdown(f"<h4 style = 'text-align: center; color: red;'>Order Quantity</h4>", unsafe_allow_html= True)
                st.markdown(f"<h5 style = 'text-align: center; color: blue;'>{total_order_qty} pairs</h5>", unsafe_allow_html= True)
            with col2:
                st.markdown(f"<h4 style = 'text-align: center; color: red;'>Shipped Quantity</h4>", unsafe_allow_html= True)
                st.markdown(f"<h5 style = 'text-align: center; color: blue;'>{total_shiped_qty} pairs</h5>", unsafe_allow_html= True)
            with col3:
                st.markdown(f"<h4 style = 'text-align: center; color: red;'>Balance Quantity</h4>", unsafe_allow_html= True)
                st.markdown(f"<h5 style = 'text-align: center; color: blue;'>{qty_balance} pairs</h5>", unsafe_allow_html= True)
            with col4:
                st.markdown(f"<h4 style = 'text-align: center; color: red;'>Order Completion</h4>", unsafe_allow_html= True)
                st.markdown(f"<h5 style = 'text-align: center; color: blue;'>{int((total_shiped_qty/total_order_qty)*100)}%</h5>", unsafe_allow_html= True)
            with col5:
                st.markdown(f"<h4 style = 'text-align: center; color: red;'>Customer</h4>", unsafe_allow_html= True)
                st.markdown(f"<h5 style = 'text-align: center; color: blue;'>{sales_df['custname'].dropna().unique()[0]}</h5>", unsafe_allow_html= True)

            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.markdown(f"<h4 style = 'text-align: center; color: red;'>Order Date</h4>", unsafe_allow_html= True)
                st.markdown(f"<h5 style = 'text-align: center; color: blue;'>{pd.to_datetime(sales_df['orderdate'].unique()[0]).strftime('%d %b, %Y')}</h5>", unsafe_allow_html= True)
            with col2:
                st.markdown(f"<h4 style = 'text-align: center; color: red;'>Due Date</h4>", unsafe_allow_html= True)
                st.markdown(f"<h5 style = 'text-align: center; color: blue;'>{pd.to_datetime(sales_df['duedate'].unique()[0]).strftime('%d %b, %Y')}</h5>", unsafe_allow_html= True)
            with col3:
                try: 
                    shipdate = pd.to_datetime(sales_df['shipdate'].unique()[0]).strftime('%d %b, %Y')
                except: 
                    shipdate = "Not Available"
                st.markdown(f"<h4 style = 'text-align: center; color: red;'>Ship Date</h4>", unsafe_allow_html= True)
                st.markdown(f"<h5 style = 'text-align: center; color: blue;'>{shipdate}</h5>", unsafe_allow_html= True)
            with col4:
                try: 
                    invoicedate = pd.to_datetime(sales_df['invoicedate'].unique()[0]).strftime('%d %b, %Y')
                except: 
                    invoicedate = "Not Available"
                st.markdown(f"<h4 style = 'text-align: center; color: red;'>Invoice Date</h4>", unsafe_allow_html= True)
                st.markdown(f"<h5 style = 'text-align: center; color: blue;'>{invoicedate}</h5>", unsafe_allow_html= True)
            with col5:
                try: 
                    vesseldate = pd.to_datetime(sales_df['vesseldate'].unique()[0]).strftime('%d %b, %Y')
                except: 
                    vesseldate = "Not Available"
                st.markdown(f"<h4 style = 'text-align: center; color: red;'>Vessel Sailing Date</h4>", unsafe_allow_html= True)
                st.markdown(f"<h5 style = 'text-align: center; color: blue;'>{vesseldate}</h5>", unsafe_allow_html= True)

            
            sales_eda = EDA(sales_df)
            col1, col2 = st.columns(2)
            col1.plotly_chart(sales_eda.stack_or_group_chart(categories = 'size', aggfunc ='sum', orientation = 'h',
                                        barmode = 'group', values = ['Price(USD)','order_qty','Delayed Qty', 'shipped_qty'], title = 'Size wise Price and Quantity Comparison'))
            col2.plotly_chart(sales_eda.piechart(categories = 'size', values = 'shipped_qty', title = "Product Shipment Ratio"))

            st.subheader("Sales Transactions")
                
            #sales_df_t = sales_df_t.drop(columns=["Unnamed: 0"])
            AgGrid(sales_df)
            df_xlsx = helper.to_excel(sales_df)
            st.download_button(label='📥 Download Dataset',
                                data=df_xlsx ,
                                file_name= 'SalesDataTransactional.xlsx')
            userManagement.app_logger(username, "Sales Dashboard Transactional")
        except Exception as e:
            raise e
            st.error(f"Sorry {str.title(username)}, could not process your request at the momenet, please contact admin if the problem persists.😟")
def render_last_invoice(username):
    try:
        st.write(fh.format_st_button(), unsafe_allow_html=True)
        st.markdown(hover_size(), unsafe_allow_html=True)
        sales_df = sales_helper.load_sales_invoice_data()
        last_wd = sales_df['invoicedate'].max()
        st.header(f'Last Invoice - {last_wd.strftime("%d %b, %Y")}')
        sales_df = sales_df[sales_df['invoicedate'] == last_wd]

        total_order_qty = int(sales_df['order_qty'].sum())
        total_shiped_qty = int(sales_df['shipped_qty'].sum())
        qty_balance = total_order_qty - total_shiped_qty

        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.markdown(f"<h4 style = 'text-align: center; color: red;'>Invoice Number</h4>", unsafe_allow_html= True)
            st.markdown(f"<h5 style = 'text-align: center; color: blue;'>{sales_df['custumInvoiceNo'].unique()}</h5>", unsafe_allow_html= True)
        with col2:
            st.markdown(f"<h4 style = 'text-align: center; color: red;'>Customer PO</h4>", unsafe_allow_html= True)
            st.markdown(f"<h5 style = 'text-align: center; color: blue;'>{sales_df['custponumber'].unique()}</h5>", unsafe_allow_html= True)
        with col3:
            st.markdown(f"<h4 style = 'text-align: center; color: red;'>BHVN PO</h4>", unsafe_allow_html= True)
            st.markdown(f"<h5 style = 'text-align: center; color: blue;'>{sales_df['bhvnpo'].unique()}</h5>", unsafe_allow_html= True)
        with col4:
            st.markdown(f"<h4 style = 'text-align: center; color: red;'>Target Lead time</h4>", unsafe_allow_html= True)
            st.markdown(f"<h5 style = 'text-align: center; color: blue;'>{int(sales_df['target_lead_time'].mean())} days</h5>", unsafe_allow_html= True)
        with col5:
            st.markdown(f"<h4 style = 'text-align: center; color: red;'>Actual Lead time</h4>", unsafe_allow_html= True)
            st.markdown(f"<h5 style = 'text-align: center; color: blue;'>{int(sales_df['actual_lead_time'].mean())} days</h5>", unsafe_allow_html= True)


        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.markdown(f"<h4 style = 'text-align: center; color: red;'>Order Quantity</h4>", unsafe_allow_html= True)
            st.markdown(f"<h5 style = 'text-align: center; color: blue;'>{total_order_qty} pairs</h5>", unsafe_allow_html= True)
        with col2:
            st.markdown(f"<h4 style = 'text-align: center; color: red;'>Shipped Quantity</h4>", unsafe_allow_html= True)
            st.markdown(f"<h5 style = 'text-align: center; color: blue;'>{total_shiped_qty} pairs</h5>", unsafe_allow_html= True)
        with col3:
            st.markdown(f"<h4 style = 'text-align: center; color: red;'>Balance Quantity</h4>", unsafe_allow_html= True)
            st.markdown(f"<h5 style = 'text-align: center; color: blue;'>{qty_balance} pairs</h5>", unsafe_allow_html= True)
        with col4:
            st.markdown(f"<h4 style = 'text-align: center; color: red;'>Order Completion</h4>", unsafe_allow_html= True)
            st.markdown(f"<h5 style = 'text-align: center; color: blue;'>{int((total_shiped_qty/total_order_qty)*100)}%</h5>", unsafe_allow_html= True)
        with col5:
            st.markdown(f"<h4 style = 'text-align: center; color: red;'>Customer</h4>", unsafe_allow_html= True)
            st.markdown(f"<h5 style = 'text-align: center; color: blue;'>{sales_df['custname'].dropna().unique()[0]}</h5>", unsafe_allow_html= True)

        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.markdown(f"<h4 style = 'text-align: center; color: red;'>Order Date</h4>", unsafe_allow_html= True)
            try: 
                order_date = pd.to_datetime(sales_df['orderdate'].unique()[0]).strftime('%d %b, %Y') 
            except: 
                order_date = "Not Available"
            st.markdown(f"<h5 style = 'text-align: center; color: blue;'>{order_date}</h5>", unsafe_allow_html= True)
        with col2:
            st.markdown(f"<h4 style = 'text-align: center; color: red;'>Due Date</h4>", unsafe_allow_html= True)
            try: 
                due_date = pd.to_datetime(sales_df['duedate'].unique()[0]).strftime('%d %b, %Y') 
            except: 
                due_date = "Not Available"
            st.markdown(f"<h5 style = 'text-align: center; color: blue;'>{due_date}</h5>", unsafe_allow_html= True)
        with col3:
            st.markdown(f"<h4 style = 'text-align: center; color: red;'>Ship Date</h4>", unsafe_allow_html= True)
            try: 
                ship_date = pd.to_datetime(sales_df['shipdate'].unique()[0]).strftime('%d %b, %Y') 
            except: 
                ship_date = "Not Available"
            st.markdown(f"<h5 style = 'text-align: center; color: blue;'>{ship_date}</h5>", unsafe_allow_html= True)
        with col4:
            st.markdown(f"<h4 style = 'text-align: center; color: red;'>Invoice Date</h4>", unsafe_allow_html= True)
            try: 
                invoice_date = pd.to_datetime(sales_df['invoicedate'].unique()[0]).strftime('%d %b, %Y') 
            except: 
                invoice_date = "Not Available"
            st.markdown(f"<h5 style = 'text-align: center; color: blue;'>{invoice_date}</h5>", unsafe_allow_html= True)
        with col5:
            st.markdown(f"<h4 style = 'text-align: center; color: red;'>Vessel Sailing Date</h4>", unsafe_allow_html= True)
            try: 
                vessel_date = pd.to_datetime(sales_df['vesseldate'].unique()[0]).strftime('%d %b, %Y') 
            except: 
                vessel_date = "Not Available"
            st.markdown(f"<h5 style = 'text-align: center; color: blue;'>{vessel_date}</h5>", unsafe_allow_html= True)

        sales_eda = EDA(sales_df)
        col1, col2 = st.columns(2)
        col1.plotly_chart(sales_eda.stack_or_group_chart(categories = 'size', aggfunc ='sum', orientation = 'h',
                                        barmode = 'group', values = ['Price(USD)','order_qty','Delayed Qty', 'shipped_qty'], title = 'Size wise Price and Quantity Comparison'))
        col2.plotly_chart(sales_eda.piechart(categories = 'size', values = 'shipped_qty', title = "Product Shipment Ratio"))

        st.subheader("Sales Last Invoice")
            
        #sales_df_t = sales_df_t.drop(columns=["Unnamed: 0"])
        AgGrid(sales_df)
        df_xlsx = helper.to_excel(sales_df)
        st.download_button(label='📥 Download Dataset',
                            data=df_xlsx ,
                            file_name= 'SalesDataLastWorkingDay.xlsx')
        userManagement.app_logger(username, "Sales Last Invoice")
    except Exception as e:
        st.error(f"Sorry {str.title(username)}, could not process your request at the momenet, please contact admin if the problem persists.😟")

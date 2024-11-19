import streamlit as st
from common import vizHelper
from st_aggrid import AgGrid
from orderStatusPckg import status_helper
import plotly.express as px
import pandas as pd
import adminPckg.userManagement as userManagement
from static.formatHelper import hover_size
from vizpool.interactive import EDA

def render_overall_status(username):
    try:
        st.markdown(hover_size(), unsafe_allow_html=True)
        #po_time_selection = st.selectbox("PO Creation Time", ['Last Week POs', 'Last One Month POs', 'Last Six Month POs', 'Last One Year POs', 'All POs from beginning'])
        st.write('<style>div.row-widget.stRadio > div{flex-direction:row;} </style>', unsafe_allow_html=True)
        st.write('<style>div.st-bf{flex-direction:column;} div.st-ag{font-weight:bold;padding-left:2px;}</style>', unsafe_allow_html=True)
        po_time_selection = st.radio("",('Last Week POs', 'Last One Month POs', 'Last Six Month POs', 'Last One Year POs', 'All POs from beginning'))
        po_time_selection = status_helper.get_po_selection_date(po_time_selection)
        col1, col2, col3 = st.columns(3)
        with col1:
            all_customers = status_helper.get_customers(po_time_selection)
            all_customers = all_customers[all_customers['Customer']!='']['Customer']
            all_customers_list = all_customers.tolist()
            all_customers_list.insert(0, "All Customers") 
            customer_selection = st.multiselect("Customer", all_customers_list, all_customers_list[0] )
            if customer_selection[0] == "All Customers" and len(customer_selection) == 1:
                customer_selection = all_customers
        all_pos = status_helper.get_all_customer_pos()
        all_pos['Date'] = all_pos['Date'].astype('datetime64[ns]')
        mask = (all_pos['Customer'].isin(customer_selection) & (all_pos['Date'] >= po_time_selection))
        all_pos = all_pos.loc[mask]
        with col2:
            po_selection = st.selectbox("Customer PO",all_pos['PO'].unique()[::-1])
            #if "selected_po_for_overall_status" not in st.session_state:
            st.session_state["selected_po_for_overall_status"] = po_selection
        with col3:
            all_items = status_helper.get_item(po_selection)
            all_items = all_items['description'].tolist()
            item_selection_default = f"All Articles in {po_selection}"
            all_items.insert(0, item_selection_default)
            item_selection = st.multiselect("Article", all_items, default= item_selection_default )
            if (item_selection_default in item_selection) & (len(item_selection) == 1) :
                item_selection = all_items
    except Exception as e:
        raise e
        st.error(f"Dear {username}, something went wrong with your selection. Contact Admin if the problem persists, we are sorry 😟")
    if st.button('Build Dashboard 📈'):
        with st.spinner(f'Please stay with us while we run the calculations for {po_selection}'):
            (purchaseStart, purchaseEnd, purchase_leadtime,min_date_sewing,max_date_sewing, sewing_leadtime, min_date_cutting, max_date_cutting, cutting_leadtime,
            min_date_auto, max_date_auto,auto_leadtime, min_date_printing, max_date_printing, printing_leadtime, min_date_issuance, max_date_issuance,
            issuance_leadtime,fin_leadtime,max_date_fin, min_date_fin, packing_leadtime, max_date_packing,min_date_packing, max_date_sales, min_date_sales, 
            sales_lead_time, cutting_status, printing_status, auto_status,issuance_status, sewing_status,fin_status, packing_status, sales_df, purchase_order_qty, purchase_rcv,
            max_date_log, min_date_log, log_leadtime, log_status) = status_helper.get_status_vars(po_selection, item_selection)
        total_order_qty = sales_df['itemqtyorder'].sum()
        '''
        try:
            purchase_order = purchase_status['Ordered Qty'][0]
        except:
            purchase_order = 0

        try:
            purchase_done = purchase_status['Received Qty'][0]
            AgGrid(purchase_status)
        except KeyError:
            purchase_done = 0
        except:
            #st.warning("System did not like the behavior of purchase_done, please contact admin")
            purchase_done = 0 
        '''
        try:
            purchase_pct_complete = round(( purchase_rcv/purchase_order_qty)*100,0)
        except ZeroDivisionError:
            purchase_pct_complete = 0
        except TypeError:
            purchase_pct_complete = 0

        cutting_done, cutting_pct_complete = status_helper.get_qty_done(cutting_status, total_order_qty)
        printing_done, printing_pct_complete = status_helper.get_qty_done(printing_status, total_order_qty) 
        auto_done, auto_pct_complete = status_helper.get_qty_done(auto_status, total_order_qty) 
        issuance_done, issuance_pct_complete = status_helper.get_qty_done(issuance_status, total_order_qty)
        sewing_done, sewing_pct_complete = status_helper.get_qty_done(sewing_status, total_order_qty)
        fin_done, fin_pct_complete = status_helper.get_qty_done(fin_status, total_order_qty)
        packing_done, packing_pct_complete = status_helper.get_qty_done(packing_status, total_order_qty)
        log_done, log_pct_complete = status_helper.get_qty_done(log_status, total_order_qty)
        total_produced = log_done
        total_pct_complete = round((total_produced/total_order_qty)*100, 1)
        sewing_wip = issuance_done - sewing_done
        df_ghantt = pd.DataFrame([
            dict(Department="Sales", Start=min_date_sales, Finish=max_date_sales, Completion_pct=total_pct_complete, LeadTime=str(sales_lead_time), OrderQty = total_order_qty, OutputQty = log_done),
            dict(Department="Purchase", Start=purchaseStart, Finish=purchaseEnd, Completion_pct=purchase_pct_complete, LeadTime=str(purchase_leadtime), OrderQty = purchase_order_qty, OutputQty = purchase_rcv),
            dict(Department="Cutting", Start=min_date_cutting, Finish=max_date_cutting, Completion_pct=cutting_pct_complete, LeadTime=str(cutting_leadtime), OrderQty = total_order_qty, OutputQty = cutting_done),
            dict(Department="Printing", Start=min_date_printing, Finish=max_date_printing, Completion_pct=printing_pct_complete, LeadTime=str(printing_leadtime), OrderQty = total_order_qty, OutputQty = printing_done),
            dict(Department="Automation", Start=min_date_auto, Finish=max_date_auto, Completion_pct=auto_pct_complete, LeadTime=str(auto_leadtime), OrderQty = total_order_qty, OutputQty = auto_done),
            dict(Department="Issuance", Start=min_date_issuance, Finish=max_date_issuance, Completion_pct=issuance_pct_complete, LeadTime=str(issuance_leadtime), OrderQty = total_order_qty, OutputQty = issuance_done),
            dict(Department="Sewing", Start=min_date_sewing, Finish=max_date_sewing, Completion_pct=sewing_pct_complete, LeadTime=str(sewing_leadtime), OrderQty = total_order_qty, OutputQty = sewing_done),
            dict(Department="Final Inspection", Start=min_date_fin, Finish=max_date_fin, Completion_pct=fin_pct_complete, LeadTime=str(fin_leadtime), OrderQty = total_order_qty, OutputQty = fin_done),
            dict(Department="Packing", Start=min_date_packing, Finish=max_date_packing, Completion_pct=packing_pct_complete, LeadTime=str(packing_leadtime), OrderQty = total_order_qty, OutputQty = packing_done),
            dict(Department="Logistics", Start=min_date_log, Finish=max_date_log, Completion_pct=log_pct_complete, LeadTime=str(log_leadtime), OrderQty = total_order_qty, OutputQty = log_done)

        ]) 
        df_ghantt = df_ghantt.dropna(subset= ['Start', 'Finish'])
        df_ghantt['LeadTime'] = df_ghantt['LeadTime'].apply(lambda x : x + " day" if x=="1" or x == "0" else x + " days")
        df_ghantt['Status'] = df_ghantt.apply(status_helper.get_status, axis=1)

        order_start_date = df_ghantt.dropna(subset=['Start'])['Start'].min() 
        order_end_date = df_ghantt.dropna(subset=['Finish'])['Finish'].max() 
        order_entry_date = sales_df['bhvnorderentrydate'].unique()[0]

        try:
            mfg_lead_time = (max_date_sewing - order_start_date).days
        except:
            mfg_lead_time = 0
        try:
            if pd.notnull(max_date_log):
                total_lead_time = (max_date_log - order_start_date).days
            else:
                total_lead_time = (order_end_date - order_start_date).days
        except:
            total_lead_time = 0
        
        if  total_produced >= total_order_qty:
            df_ghantt['Status'] = "Closed"
            order_status = "Closed"
        else:
            order_status = "Open"

        try:
            order_entry_date = order_entry_date.strftime('%d %b, %Y')
        except:
            pass
        try:
            min_date_sales = min_date_sales.strftime('%d %b, %Y')
        except:
            pass
        try:
            max_date_sales = max_date_sales.strftime('%d %b, %Y') 
        except:
            pass

        col1, col2, col3, col4, col5 = st.columns(5) 
        with col1: 
            st.markdown(f"<h5 style = 'text-align: center; color: red;'>Cutomer PO</h5>", unsafe_allow_html= True)
            st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{po_selection}</h4>", unsafe_allow_html= True)
        with col2: 
            st.markdown(f"<h5 style = 'text-align: center; color: red;'>Sales PO</h5>", unsafe_allow_html= True)
            st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{sales_df['orderid'].unique()[0]}</h4>", unsafe_allow_html= True)
        with col3:
            st.markdown(f"<h5 style = 'text-align: center; color: red;'>BHVN PO</h5>", unsafe_allow_html= True)
            st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{sales_df['ProductionNo'].unique()[0]}</h4>", unsafe_allow_html= True)
        with col4:
            st.markdown(f"<h5 style = 'text-align: center; color: red;'>Order Entry</h5>", unsafe_allow_html= True)
            st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{order_entry_date}</h4>", unsafe_allow_html= True)
        with col5:
            st.markdown(f"<h5 style = 'text-align: center; color: red;'>Order Start</h5>", unsafe_allow_html= True)
            st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{min_date_sales}</h4>", unsafe_allow_html= True)
        
        col1, col2, col3, col4, col5 = st.columns(5) 
        with col1:
            st.markdown(f"<h5 style = 'text-align: center; color: red;'>Due Date</h5>", unsafe_allow_html= True)
            st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{max_date_sales}</h4>", unsafe_allow_html= True)
        with col2:
            st.markdown(f"<h5 style = 'text-align: center; color: red;'>Sewing WIP</h5>", unsafe_allow_html= True)
            st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{int(sewing_wip)} pairs</h4>", unsafe_allow_html= True)
        with col3: 
            st.markdown(f"<h5 style = 'text-align: center; color: red;'>Total Order</h5>", unsafe_allow_html= True)
            st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{int(total_order_qty)} pairs</h4>", unsafe_allow_html= True)
        with col4: 
            st.markdown(f"<h5 style = 'text-align: center; color: red;'>Total Output</h5>", unsafe_allow_html= True)
            st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{total_produced} pairs</h4>", unsafe_allow_html= True)
        with col5:
            st.markdown(f"<h5 style = 'text-align: center; color: red;'>Order Status</h5>", unsafe_allow_html= True)
            st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{order_status}</h4>", unsafe_allow_html= True)
        
        col1, col2, col3, col4, col5 = st.columns(5) 
        with col1:
            st.markdown(f"<h5 style = 'text-align: center; color: red;'>Percent Complete</h5>", unsafe_allow_html= True)
            st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{total_pct_complete} %</h4>", unsafe_allow_html= True)
        with col2:
            st.markdown(f"<h5 style = 'text-align: center; color: red;'>Required Lead time</h5>", unsafe_allow_html= True)
            st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{sales_lead_time} days</h4>", unsafe_allow_html= True)
        with col3:
            st.markdown(f"<h5 style = 'text-align: center; color: red;'>Mfg Lead time</h5>", unsafe_allow_html= True)
            st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{mfg_lead_time} days</h4>", unsafe_allow_html= True)
        with col4:
            st.markdown(f"<h5 style = 'text-align: center; color: red;'>Logistics Lead time</h5>", unsafe_allow_html= True)
            st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{log_leadtime} days</h4>", unsafe_allow_html= True)
        with col5:
            st.markdown(f"<h5 style = 'text-align: center; color: red;'>End-to-End Lead time</h5>", unsafe_allow_html= True)
            st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{total_lead_time} days</h4>", unsafe_allow_html= True)
    
        col1, col2 = st.columns(2)
        ghantt_title = f'Manufacturing Life Cycle of {po_selection}'
        fig = px.timeline(df_ghantt, x_start="Start", x_end="Finish", y="Department", color="Completion_pct",width=600,height=500, hover_name = 'Department',
         hover_data=["LeadTime","Status", "OrderQty", "OutputQty"], text = "Department",title=ghantt_title, color_continuous_scale=["red","yellow", "green"])
        fig.update_yaxes(autorange="reversed")
        col1.plotly_chart(fig)
        group_chart_title = f'Department wise Percent Completion of {po_selection}'
        #df_ghantt_instance = EDA(df_ghantt)
        #col1.plotly_chart(df_ghantt_instance.stack_or_group_chart(categories='Department', values =['Completion_pct'], sort_by = 'Completion_pct',
        #                        barmode='group',orientation='v',aggfunc='mean', width = 600, height = 500, title = ''))
        col2.plotly_chart(vizHelper.stack_or_group_chart_px(df_ghantt.sort_values(by='Completion_pct', ascending = True),'Department', 'Completion_pct', color = 'Status' , barmode="stack", orientation="h", height=500, width = 600, color_sequence= ["red", "green"],title=group_chart_title, hover_data = ['OrderQty', 'OutputQty']))
        st.subheader(f'Order Status of {po_selection}')
        AgGrid(df_ghantt)
        userManagement.app_logger(username, "Overall Status")

        

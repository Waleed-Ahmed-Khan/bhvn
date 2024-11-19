import streamlit as st
from common import vizHelper
from st_aggrid import AgGrid
from orderStatusPckgNew import status_helper
import plotly.express as px
import pandas as pd
import adminPckg.userManagement as userManagement
from static.formatHelper import hover_size
from vizpool.interactive import EDA
import numpy as np


def render_overall_status_transactions(username):
    try:
        st.markdown(hover_size(), unsafe_allow_html=True)
        #po_time_selection = st.selectbox("PO Creation Time", ['Last Week POs', 'Last One Month POs', 'Last Six Month POs', 'Last One Year POs', 'All POs from beginning'])
        st.write('<style>div.row-widget.stRadio > div{flex-direction:row;} </style>', unsafe_allow_html=True)
        st.write('<style>div.st-bf{flex-direction:column;} div.st-ag{font-weight:bold;padding-left:2px;}</style>', unsafe_allow_html=True)
        po_time_selection = st.radio("",('Last Week POs', 'Last One Month POs', 'Last Six Month POs', 'Last One Year POs', 'All POs from beginning'))
        po_time_selection = status_helper.get_po_selection_date(po_time_selection)
        col1, col2 = st.columns(2)
        with col1:
            all_customers = status_helper.get_customers(po_time_selection)
            all_customers = all_customers[all_customers['Customer']!='']['Customer']
            all_customers_list = all_customers.tolist()
            all_customers_list.insert(0, "All Customers") 
            customer_selection = st.multiselect("Customers", all_customers_list, all_customers_list[0] )
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
    except Exception as e:
        #raise e
        st.error(f"Dear {username}, something went wrong with your selection. Contact Admin if the problem persists, we are sorry 😟")
    if st.button('Build Dashboard 📈'):

        df_ghantt = status_helper.get_po_df(po_selection)
        issuance_done = df_ghantt[df_ghantt['Department']=="Issuance"]["OutputQty"].values
        sewing_done = df_ghantt[df_ghantt['Department']=="Sewing"]["OutputQty"].values
        log_done = df_ghantt[df_ghantt['Department']=="Logistics"]["OutputQty"].values
        total_produced = log_done
        total_order_qty = df_ghantt[df_ghantt['Department']=="Sales"]["OrderQty"].values[0]

        if total_produced !=0:
            total_produced = total_produced[0]
        else:
            total_produced = 0

        total_pct_complete = (total_produced/total_order_qty)*100

        sewing_wip = issuance_done - sewing_done
        
        df_ghantt = df_ghantt.dropna(subset= ['Start', 'Finish'])
        df_ghantt['LeadTime'] = df_ghantt['LeadTime'].apply(lambda x : x + " day" if x=="1" or x == "0" else x + " days")
        df_ghantt['Status'] = df_ghantt.apply(status_helper.get_status, axis=1)

        order_start_date = df_ghantt[df_ghantt['Department']=="Target"]["Start"].values
        print(order_start_date)
        order_end_date = df_ghantt[df_ghantt['Department']=="Target"]["Finish"].values
        #order_entry_date = sales_df['bhvnorderentrydate'].unique()[0]
        max_date_sewing = df_ghantt[df_ghantt['Department']=="Sewing"]["Finish"].values
        max_date_log = df_ghantt[df_ghantt['Department']=="Logistics"]["Finish"].values
        try:
            if pd.notnull(max_date_sewing):
                mfg_lead_time = (max_date_sewing[0] - order_start_date[0]).days
            else:
                mfg_lead_time = 0
        except Exception as e:
            #raise e
            mfg_lead_time = 0

        try:
            if pd.notnull(max_date_sewing) and pd.notnull(max_date_log):
                log_lead_time = (max_date_log[0] - max_date_sewing[0]).days
            else:
                log_lead_time = 0
        except:
            log_lead_time = 0

        try:
            if pd.notnull(max_date_log):
                total_lead_time = (max_date_log[0] - order_start_date[0]).days
            else:
                total_lead_time = 0
        except:
            total_lead_time = 0

        sales_lead_time = (order_end_date[0] - order_start_date[0]).days
        
        if  total_produced >= total_order_qty:
            df_ghantt['Status'] = "Closed"
            order_status = "Closed"
        else:
            order_status = "Open"

        

        # try:
        #     order_entry_date = order_entry_date.strftime('%d %b, %Y')
        # except:
        #     pass
        try:
            min_date_sales = (pd.to_datetime(order_start_date)).strftime('%d %b, %Y')[0]
        except Exception as e:
            #raise e
            pass
        try:
            max_date_sales = (pd.to_datetime(order_end_date)).strftime('%d %b, %Y')[0]
        except:
            pass

        col1, col2, col3, col4 = st.columns(4) 
        with col1: 
            st.markdown(f"<h5 style = 'text-align: center; color: red;'>Cutomer PO</h5>", unsafe_allow_html= True)
            st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{po_selection}</h4>", unsafe_allow_html= True)
        with col2:
            st.markdown(f"<h5 style = 'text-align: center; color: red;'>Due Date</h5>", unsafe_allow_html= True)
            st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{max_date_sales}</h4>", unsafe_allow_html= True)
        with col3:
            st.markdown(f"<h5 style = 'text-align: center; color: red;'>Order Status</h5>", unsafe_allow_html= True)
            st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{order_status}</h4>", unsafe_allow_html= True)
        with col4:
            st.markdown(f"<h5 style = 'text-align: center; color: red;'>Order Start</h5>", unsafe_allow_html= True)
            st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{min_date_sales}</h4>", unsafe_allow_html= True)
        
        col1, col2, col3, col4 = st.columns(4) 

        with col1: 
            st.markdown(f"<h5 style = 'text-align: center; color: red;'>Total Order</h5>", unsafe_allow_html= True)
            st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{int(total_order_qty)} pairs</h4>", unsafe_allow_html= True)
        with col2: 
            st.markdown(f"<h5 style = 'text-align: center; color: red;'>Total Output</h5>", unsafe_allow_html= True)
            st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{int(total_produced)} pairs</h4>", unsafe_allow_html= True)

        with col3:
            st.markdown(f"<h5 style = 'text-align: center; color: red;'>Sewing WIP</h5>", unsafe_allow_html= True)
            st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{int(sewing_wip)} pairs</h4>", unsafe_allow_html= True)
        with col4:
            st.markdown(f"<h5 style = 'text-align: center; color: red;'>Percent Complete</h5>", unsafe_allow_html= True)
            st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{total_pct_complete} %</h4>", unsafe_allow_html= True)
        
        col1, col2, col3, col4 = st.columns(4) 
        with col1:
            st.markdown(f"<h5 style = 'text-align: center; color: red;'>Required Lead time</h5>", unsafe_allow_html= True)
            st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{sales_lead_time} days</h4>", unsafe_allow_html= True)
        with col2:
            st.markdown(f"<h5 style = 'text-align: center; color: red;'>Mfg Lead time</h5>", unsafe_allow_html= True)
            st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{mfg_lead_time} days</h4>", unsafe_allow_html= True)
        with col3:
            st.markdown(f"<h5 style = 'text-align: center; color: red;'>Logistics Lead time</h5>", unsafe_allow_html= True)
            st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{log_lead_time} days</h4>", unsafe_allow_html= True)
        with col4:
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
        #userManagement.app_logger(username, "Overall Status Transactional")

        
def render_overall_status_strategic(username):
    
    try:
        st.markdown(hover_size(), unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        customers_and_mastercodes = status_helper.get_all_mastercodes()
        with col1:
            all_customers = customers_and_mastercodes[customers_and_mastercodes['Customer']!='']['Customer']
            all_customers_list = all_customers.unique().tolist()
            all_customers_list.insert(0, "All Customers") 
            customer_selection = st.multiselect("Customer", all_customers_list, all_customers_list[0] )
            if customer_selection[0] == "All Customers" and len(customer_selection) == 1:
                customer_selection = all_customers_list
        with col2:
            
            all_mastercodes_list = customers_and_mastercodes['MasterCode'].unique().tolist()
            all_mastercodes_list.insert(0, "All Mastercodes")
            mastercode_selection = st.multiselect("Mastercode", all_mastercodes_list, all_mastercodes_list[0])
            if mastercode_selection[0] == "All Mastercodes" and len(mastercode_selection) == 1:
                mastercode_selection = all_mastercodes_list
    except Exception as e:
        raise e
        st.error(f"Dear {username}, something went wrong with your selection. Contact Admin if the problem persists, we are sorry 😟")
    if st.button('Build Dashboard 📈', key = 123):

        df_ghantt = status_helper.get_strategic_df(customer_selection, mastercode_selection)
        if df_ghantt.empty:
            st.info("Not a valid selection, please select different values")
        df_ghantt['LeadTime'] = np.where(pd.isnull(df_ghantt['Start']), np.nan, df_ghantt['LeadTime'])
        df_ghantt = df_ghantt.dropna(subset=['LeadTime']) 
        df_ghantt = df_ghantt.astype({'LeadTime': float})

        df_ghantt = df_ghantt[['Department', 'LeadTime']].groupby('Department', as_index = False).mean()
        avg_dep_lead_time = round(float(df_ghantt['LeadTime'].mean()), 0)
        avg_total_lead_time = round(float(df_ghantt['LeadTime'].sum()), 0)

        col1, col2 = st.columns(2) 
        with col1:
            st.markdown(f"<h5 style = 'text-align: center; color: red;'>Avg of total Lead-time</h5>", unsafe_allow_html= True)
            st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{avg_total_lead_time} days</h4>", unsafe_allow_html= True)
            with st.expander("Formula"):
                st.latex(r'''
                =\left(\frac{Σ LeadTime}{Σ Orders}\right)
                ''')
        with col2:
            st.markdown(f"<h5 style = 'text-align: center; color: red;'>Department wise avg Lead-time</h5>", unsafe_allow_html= True)
            st.markdown(f"<h4 style = 'text-align: center; color: blue;'>{avg_dep_lead_time} days</h4>", unsafe_allow_html= True)
            with st.expander("Formula"):
                st.latex(r'''
                =\left(\frac{Σ LeadTimePerDepartment}{Σ OrdersPerDepartment}\right)
                ''')
        ghantt_title = f'Department wise average leadtime'
        eda_lt = EDA(df_ghantt.round(0))
        
        # fig = px.timeline(df_ghantt, x_start="Start", x_end="Finish", y="Department", color="Completion_pct",width=600,height=500, hover_name = 'Department',
        #  hover_data=["LeadTime","Status", "OrderQty", "OutputQty"], text = "Department",title=ghantt_title, color_continuous_scale=["red","yellow", "green"])
        # fig.update_yaxes(autorange="reversed")
        # col1.plotly_chart(fig)
        # group_chart_title = f'Department wise Percent Completion of {po_selection}'
        #df_ghantt_instance = EDA(df_ghantt)
        #col1.plotly_chart(df_ghantt_instance.stack_or_group_chart(categories='Department', values =['Completion_pct'], sort_by = 'Completion_pct',
        #                        barmode='group',orientation='v',aggfunc='mean', width = 600, height = 500, title = ''))
        st.plotly_chart(eda_lt.stack_or_group_chart(values=["LeadTime"], height=600, width=900, title = 'Department wise Avg Lead-time',
                                                    categories='Department', orientation='h', unit="days", sort_by='LeadTime'))
        st.subheader('Department wise Avg Lead-time')
        df_ghantt = df_ghantt.sort_values('LeadTime', ascending = False)
        AgGrid(df_ghantt.round(0))
        #userManagement.app_logger(username, "Overall Status Strategic")
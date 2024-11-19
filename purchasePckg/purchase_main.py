import streamlit as st
from common import helper, vizHelper
import adminPckg.userManagement as userManagement
import pandas as pd
import plotly.graph_objects as go
import static.formatHelper as fh
import purchasePckg.purchase as purchase 
import numpy as np 
from st_aggrid import AgGrid
from static.formatHelper import hover_size
from vizpool.interactive import EDA


def render_purchase_operations(username):
    st.markdown(hover_size(), unsafe_allow_html=True)
    with st.form(key="purhcase_form"):
        purch, date, purchase_po_list, purch_order_status, year, customer_po_list, vendor_list, categories_list, source = purchase.get_purchase_variables()
        
        st.write(fh.format_st_button(), unsafe_allow_html=True)

        col1,col2,col3,col4, col5 =  st.columns(5)
        with col1:
            st.markdown("**Purchase Order**")
            po_selection = st.multiselect('',  purchase_po_list, default='All POs')
        with col2:
            st.markdown("**Customer Order**")
            customer_po_selection = st.multiselect('', customer_po_list, default = "All POs" )
        with col3:
            st.markdown("**Order Status**")
            purch_order_status = st.multiselect('',purch_order_status,default= purch_order_status)
        with col4:
            st.markdown("**Vendor**")
            vendor_selection = st.multiselect('',vendor_list, default = "All Vendors")
        with col5:
            st.markdown("**Import/Local**")
            source_selection = st.multiselect('',source, default = source)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown("**Start Date :**")
            start_date = st.date_input('', min(date))
        with col2:
            st.markdown("**End Date :**")
            end_date = st.date_input('', max(date))
        with col3:
            st.markdown("**Year**")
            year = st.selectbox('',year)
        with col4:
            st.markdown("**Material Category**")
            categories_selection = st.multiselect('',categories_list, default ="All Categories")
        st.markdown('<hr/>', unsafe_allow_html = True)
        st.form_submit_button(label = '📈 Build Dashboard')

    if ('Open' in purch_order_status) and (len(purch_order_status)==1):
            purch = purch[purch['Order Status']== 'Open']
            purch = purch.append(purch.sum(numeric_only=True), ignore_index=True)
            st.info('Aggregate measures are not available for Open Orders')
            '''
            st.subheader('DataFrame Head : ')
            st.dataframe(purch.head(50).style.format({"Total Price Of Order": "₫{:20,.0f}", 
                        "Unit Price": "₫{:20,.0f}", "Ordered Qty": "{:20,.0f}"})\
                .hide_index()\
                .bar(subset=["Total Price Of Order",], color='lightgreen')\
                .bar(subset=["Unit Price"], color='#a4c2eb')\
                .bar(subset=["Ordered Qty"], color='#eba4e3'))

            st.subheader('DataFrame Tail : ')
            st.dataframe(purch.tail(50).style.format({"Total Price Of Order": "₫{:20,.0f}", 
                        "Unit Price": "₫{:20,.0f}", "Ordered Qty": "{:20,.0f}"})\
                .hide_index()\
                .bar(subset=["Total Price Of Order",], color='lightgreen')\
                .bar(subset=["Unit Price"], color='#a4c2eb')\
                .bar(subset=["Ordered Qty"], color='#eba4e3'))
            #purch['Total Price Of Order'] = round(purch['Total Price Of Order'], 1)
            '''
            st.subheader("Complete Dataset")
            AgGrid(data = purch, height = 20)
            st.download_button(
            '📥 Download Dataset',
            purch.to_csv( index = False ).encode('utf-8'),
            "PurchaseData.csv",
            "text/csv",
            key='download-csv'
            )
            #userManagement.app_logger(username, "Purchase Operations")
        
    else:
        if po_selection ==["All POs"]:
            po_selection = purchase_po_list
        else:
            if 'All POs' in po_selection:
                po_selection.pop(0)
        if customer_po_selection ==["All POs"]:
            customer_po_selection = customer_po_list
        else:
            if 'All POs' in customer_po_selection:
                customer_po_selection.pop(0)
        if vendor_selection == ["All Vendors"]:
            vendor_selection = vendor_list
        if categories_selection ==["All Categories"]:
            categories_selection = categories_list
        purch ,delay , Percent_Delays,combined_prc_del, Avg_Delay,lead_t, Avg_lead_time, Total_Delayed_Orders, avg_remaining_days, Total_Placed_Orders, percent_dr_vendor_score_df, avg_percent_dr, avg_vendor_score, data_for_facet, hot_df = helper.preprocess_purch(
            purch,start_date, end_date, purch_order_status, po_selection, year, customer_po_selection, vendor_selection, categories_selection, source_selection)
        if isinstance(purch, pd.DataFrame):
            if len(purch['Customer PO'].dropna().unique().tolist()) == 1:
                Avg_lead_time = (purch['Received Date'].max() - purch['Order Date'].min())/np.timedelta64(1, 'D')
            kpi1, kpi2,kpi3 =  st.columns(3)
            with kpi1:
                st.markdown(f"<h4 style = 'text-align: center; color: red;'>Avg Delay</h4>", unsafe_allow_html= True)
                st.markdown(f"<h5 style = 'text-align: center; color: blue;'>{Avg_Delay} Days</h5>", unsafe_allow_html= True)
                with st.expander("Avg Delay Formula"):
                    st.latex(r'''
                    =\left(\frac{Σ Delay (Days)}{Σ Purchase Orders}\right)
                    ''')
            with kpi2:
                st.markdown(f"<h4 style = 'text-align: center; color: red;'>Avg Lead Time</h4>", unsafe_allow_html= True)
                st.markdown(f"<h5 style = 'text-align: center; color: blue;'>{int(Avg_lead_time)} Days</h5>", unsafe_allow_html= True)
                with st.expander("Avg Lead Time Formula"):
                    st.latex(r'''
                    =\left(\frac{Σ Lead Time}{Σ Purchase Orders}\right)
                    ''')
            with kpi3:
                st.markdown(f"<h4 style = 'text-align: center; color: red;'>Avg Target Lead Time</h4>", unsafe_allow_html= True)
                st.markdown(f"<h5 style = 'text-align: center; color: blue;'>{int(purch['lead_time_req'].mean())} days</h5>", unsafe_allow_html= True)
                with st.expander("Target Lead Time Formula"):
                    st.latex(r'''
                    =\left(\frac{Σ Required Lead Time}{Σ Purchase Orders}\right)
                    ''')
            kpi1, kpi2,kpi3, kpi4 =  st.columns(4)
            with kpi1:
                st.markdown(f"<h4 style = 'text-align: center; color: red;'>% HOT (Handover on time)</h4>", unsafe_allow_html= True)
                st.markdown(f"<h5 style = 'text-align: center; color: blue;'>{round(hot_df['% HOT'].mean(), 1)} %</h5>", unsafe_allow_html= True)
                with st.expander("Handover on time Formula"):
                    st.latex(r'''
                    =\left(\frac{Σ(Qty Ontime)}{Total Qty Received}\right)*100
                    ''')
            with kpi2:
                st.markdown(f"<h4 style = 'text-align: center; color: red;'>% PO Delayed</h4>", unsafe_allow_html= True)
                st.markdown(f"<h5 style = 'text-align: center; color: blue;'>{Percent_Delays} %</h5>", unsafe_allow_html= True)
                with st.expander("% Delay Formula"):
                    st.latex(r'''
                    =\left(\frac{Σ Delayed Orders}{Σ OrdersReceived}\right) * 100
                    ''')
            with kpi3:
                st.markdown(f"<h4 style = 'text-align: center; color: red;'>Avg Defect Rate</h4>", unsafe_allow_html= True)
                st.markdown(f"<h5 style = 'text-align: center; color: blue;'>{round((avg_percent_dr*100),3)} %</h5>", unsafe_allow_html= True)
                with st.expander("Avg Defect Rate Formula"):
                    st.latex(r'''
                    =\left(\frac{Σ Defects}{Σ Purchase Orders}\right) * 100
                    ''')
            with kpi4:
                st.markdown(f"<h4 style = 'text-align: center; color: red;'>Defects Per Million</h4>", unsafe_allow_html= True)
                st.markdown(f"<h5 style = 'text-align: center; color: blue;'>{round((avg_percent_dr*1000000),6)}</h5>", unsafe_allow_html= True)
                with st.expander("DPM Formula"):
                    st.latex(r'''
                    =\left(\frac{Σ Defects}{Σ Opportunities}\right) * 1000000
                    ''')

            st.markdown('<hr/>', unsafe_allow_html = True)
            kpi1, kpi2,kpi3 =  st.columns(3)
            with kpi1:
                st.markdown(f"<h4 style = 'text-align: center; color: red;'>Total Orders Placed</h4>", unsafe_allow_html= True)
                st.markdown(f"<h5 style = 'text-align: center; color: blue;'>{Total_Placed_Orders}</h5>", unsafe_allow_html= True)

            with kpi2:
                st.markdown(f"<h4 style = 'text-align: center; color: red;'>Total Ontime Delivered</h4>", unsafe_allow_html= True)
                st.markdown(f"<h5 style = 'text-align: center; color: blue;'>{int(Total_Placed_Orders-Total_Delayed_Orders)}</h5>", unsafe_allow_html= True)

            with kpi3:
                st.markdown(f"<h4 style = 'text-align: center; color: red;'>Total Delayed Orders</h4>", unsafe_allow_html= True)
                st.markdown(f"<h5 style = 'text-align: center; color: blue;'>{int(Total_Delayed_Orders)}</h5>", unsafe_allow_html= True)

            st.markdown('<hr/>', unsafe_allow_html = True)

            col1, col2 = st.columns(2)
            delay_instance = EDA(delay)
            try:
                col1.plotly_chart(delay_instance.area_chart(categories='Month', values = 'Delay (Days)', title = 'Avg Monthly Delay (Days)', unit = "days", sort_by = 'month_num'))
            #fig = vizHelper.area_chart(delay, 'Month', 'Delay (Days)', 'Month', 'Delay', 'Monthly Avg Delay', unit = 'days')
            except: 
                pass
            lead_time_instance = EDA(lead_t)
            fig = lead_time_instance.stacked_area_chart(time = "Month", values = ['Lead Time (Days)', 'Target Lead Time (Days)'], sort_by = 'month_num',
                                                        title = "Avg Monthly Lead Time (Days)", width=600,height=450)
            #col2.plotly_chart(vizHelper.area_chart(lead_t, 'Month', 'Lead Time (Days)','Month', 'Lead Time', 'Monthly Avg Lead Time', unit = 'days'))
            col2.plotly_chart(fig)
            col1, col2 = st.columns(2)
            delay_pct_instance = EDA(combined_prc_del)
            col1.plotly_chart(delay_pct_instance.area_chart(categories='Month', values = 'Percent Delay', title = 'Month % Delay of PO delayed', unit = "%", sort_by = 'month_num'))
            #col1.plotly_chart(vizHelper.area_chart(combined_prc_del, 'Month', 'Percent Delay','Month', "% Delay", 'Month Wise % Delay', unit = "%"))
            hot_instance = EDA(hot_df)
            col2.plotly_chart(hot_instance.area_chart(categories='Month', values = '% HOT', title = 'Monthly % HOT (Handover on time)', unit = "%", sort_by = 'month_num'))
            
            st.markdown('<hr/>', unsafe_allow_html = True)
            
            col1, col2 = st.columns(2)
            cat_nature_instance = EDA(purch[purch['Delay (Days)']>0].rename(columns = {'lead_time_req': 'Required Lead Time (Days)'}))
            col1.plotly_chart(cat_nature_instance.stack_or_group_chart(categories = 'Nature', 
                                                                values = ['Lead Time (Days)', 'Delay (Days)', 'Required Lead Time (Days)'],
                                                                barmode = 'group', sort_by = 'Delay (Days)',
                                                                orientation='h', aggfunc='mean',
                                                                title = 'Material Nature wise delay and lead time analysis of Delayed POs'
                                                                ))
            col2.plotly_chart(cat_nature_instance.stack_or_group_chart(categories = 'Category', 
                                                                values = ['Lead Time (Days)', 'Delay (Days)', 'Required Lead Time (Days)'],
                                                                barmode = 'group', sort_by = 'Delay (Days)',
                                                                orientation='h', aggfunc='mean',
                                                                title = 'Material Category wise delay and lead time analysis of Delayed POs'
                                                                ))

            st.markdown('<hr/>', unsafe_allow_html = True)
            col1, col2 = st.columns(2)
            col1.plotly_chart(vizHelper.pie_chart(purch, 'Ordered Qty', 'Nature', title='Material Nature wise procurement'))
            col2.plotly_chart(vizHelper.pie_chart(purch, 'Ordered Qty', 'Category', title='Material Category wise procurement')) 
            
            st.markdown('<hr/>', unsafe_allow_html = True)
            col1, col2 = st.columns(2)
            purch['Order Date'] = purch['Order Date'].astype('datetime64').dt.strftime("%Y/%m/%d")
            col1.plotly_chart(vizHelper.combined_corr(purch.dropna(subset=['Total Price Of Order']),x="Lead Time (Days)", y="Delay (Days)", color="Category", 
                            hover_name='Customer PO',size='Total Price Of Order',title="Material Category wise Correlation of Delay and Lead Time"))
            #col2.plotly_chart(vizHelper.facetgrid(data_for_facet, cat_cols=['Category', 'Nature', 'Ontime/Delay', 'Month'], value='Lead Time (Days)', barmode= "stack", title = "Facetgrid of Avg Lead Time"))
            #st.markdown('<hr/>', unsafe_allow_html = True)
            try:
                col2.plotly_chart(cat_nature_instance.facetgrid(categories = 'Nature', values = 'Delay (Days)', color = 'Category',
                                                           facet_row = 'Ontime/Delay', facet_col = 'Month', aggfunc= 'mean',
                                                           sort_by = 'Delay (Days)', width=600,height=450, title = "Facetgrid of Avg Delay (Days)")) 
            except:
                pass
            purch = purch.append(purch.sum(numeric_only=True), ignore_index=True)
            '''
            st.subheader('DataFrame Head : ')
            st.dataframe(purch.head(50).style.format({"Total Price Of Order": "₫{:20,.0f}", 
                        "Unit Price": "₫{:20,.0f}","Ordered Qty": "{:20,.0f}"})\
                .hide_index()\
                .bar(subset=["Total Price Of Order",], color='lightgreen')\
                .bar(subset=["Unit Price"], color='#a4c2eb')\
                .bar(subset=["Ordered Qty"], color='#eba4e3'))

            st.subheader('DataFrame Tail : ')
            st.dataframe(purch.tail(50).style.format({"Total Price Of Order": "₫{:20,.0f}", 
                        "Unit Price": "₫{:20,.0f}","Ordered Qty": "{:20,.0f}"})\
                .hide_index()\
                .bar(subset=["Total Price Of Order",], color='lightgreen')\
                .bar(subset=["Unit Price"], color='#a4c2eb')\
                .bar(subset=["Ordered Qty"], color='#eba4e3'))
            #purch['Total Price Of Order'] = round(purch['Total Price Of Order'], 1)
            st.subheader("Complete Dataset")
            st.dataframe(purch)
            
            #st.dataframe(purch.style.format(subset=['Total Price Of Order', 'Unit Price'], formatter="{:.2f}"))
            '''
            st.subheader("Complete Dataset")
            AgGrid(purch)
            purch = purch.drop(['year', 'month_num', 'Month', 'Days Remaining'], axis=1)
            st.download_button(
            '📥 Download Dataset',
            purch.to_csv( index = False ).encode('utf-8'),
            "PurchaseData.csv",
            "text/csv",
            key='download-csv'
            )
            # df_xlsx = helper.to_excel(purch)
            # st.download_button(label='📥 Download Dataset',
            #                         data=df_xlsx ,
            #                         file_name= 'PurchaseData.xlsx')
            #userManagement.app_logger(username, "Purchase Operations")
        else :
            st.error(f"Dear {str.title(username)}, Please check you selection again as there seems to be a problem with the data filtering 👆. Your specific selection might not hold any data. ❌")

def render_last_working_day(username):
    st.markdown(hover_size(), unsafe_allow_html=True)
    purch, date, purchase_po_list, purch_order_status, year, customer_po_list, vendor_list, categories_list, source = purchase.get_purchase_variables()
    last_wd = purch['Order Date'].max()
    st.header(f'Last Working Day - {last_wd.strftime("%d %b, %Y")}')
    st.markdown('<hr/>', unsafe_allow_html = True)
    purch = purch[purch['Order Date'] == last_wd]
    total_qty = purch['Ordered Qty'].sum()
    total_price = purch['Total Price Of Order'].sum()
    kpi1, kpi2 =  st.columns(2)
    with kpi1:
        st.markdown(f"<h4 style = 'text-align: center; color: red;'>Target Quantity Ordered</h4>", unsafe_allow_html= True)
        st.markdown(f"<h3 style = 'text-align: center; color: blue;'>{int(total_qty)}</h3>", unsafe_allow_html= True)

    with kpi2:
        st.markdown(f"<h4 style = 'text-align: center; color: red;'>Total Price of Order</h3>", unsafe_allow_html= True)
        st.markdown(f"<h3 style = 'text-align: center; color: blue;'>{int(total_price)} ₫</h1>", unsafe_allow_html= True)

    st.markdown('<hr/>', unsafe_allow_html = True)
    AgGrid(purch)
    # st.download_button(
    # '📥 Download Dataset',purch.to_csv( index = False ).encode('utf-8'),
    # "SewingData.csv","text/csv",key='download-csv'
    # )
    df_xlsx = helper.to_excel(purch)
    st.download_button(label='📥 Download Dataset',
                            data=df_xlsx ,
                            file_name= 'PurchaseData.xlsx')
    #userManagement.app_logger(username, "Purchase LWD")

def render_vendor_analysis(username):
    st.markdown(hover_size(), unsafe_allow_html=True)
    purch, date, purchase_po_list, purch_order_status, year, customer_po_list, vendor_list, categories_list, source = purchase.get_purchase_variables()
    st.write(fh.format_st_button(), unsafe_allow_html=True)

    with st.form(key="vendor_form"):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown("**Start Date :**")
            start_date = st.date_input('', pd.to_datetime(min(date)))
        with col2:
            st.markdown("**End Date :**")
            end_date = st.date_input('', pd.to_datetime(max(date)))
        with col3:
            st.markdown("**Year**")
            year = st.selectbox('', year)
        with col4:
            st.markdown("**Vendor**")
            vendor_selection = st.multiselect('', vendor_list, default = "All Vendors" )
        st.markdown('<hr/>', unsafe_allow_html = True)
        st.form_submit_button('💥 Analyze ‼ ')

    if vendor_selection ==["All Vendors"]:
        vendor_selection = vendor_list
    #else:
    #    if 'All Vendors' in customer_po_selection:
    #        customer_po_selection.pop(0)

    _ ,_ , _,_, _,_, _, _, _, _, _, _, avg_vendor_score_all, _,  _ = helper.preprocess_purch(
        purch, start_date, end_date,purch_order_status, purchase_po_list, year, customer_po_list ,vendor_list, categories_list, source)
    purch , delay , Percent_Delays,combined_prc_del, Avg_Delay,lead_t, Avg_lead_time, Total_Delayed_Orders, avg_remaining_days, Total_Placed_Orders, percent_dr_vendor_score_df, avg_percent_dr, avg_vendor_score, _ , _= helper.preprocess_purch(
        purch, start_date, end_date, purch_order_status, purchase_po_list, year, customer_po_list , vendor_selection, categories_list, source)
    if isinstance(purch, pd.DataFrame):
            kpi1, kpi2,kpi3 =  st.columns(3)
            with kpi1:
                st.markdown(f"<h4 style = 'text-align: center; color: red;'>Avg Vendor Score</h4>", unsafe_allow_html= True)
                st.markdown(f"<h3 style = 'text-align: center; color: blue;'>{round(avg_vendor_score, 2)}</h3>", unsafe_allow_html= True)
                with st.expander("Avg Delay Formula"):
                    st.latex(r'''
                    =\left(\frac{Σ Score}{Σ Purchase Orders}\right)
                    ''')
            with kpi2:
                st.markdown(f"<h4 style = 'text-align: center; color: red;'>Avg Defect Rate</h4>", unsafe_allow_html= True)
                st.markdown(f"<h3 style = 'text-align: center; color: blue;'>{round(avg_percent_dr * 100,2)} %</h3>", unsafe_allow_html= True)
                with st.expander("Avg Lead Time Formula"):
                    st.latex(r'''
                    =\left(\frac{Σ Defects}{Σ Purchase Orders}\right)
                    ''')
            with kpi3:
                st.markdown(f"<h4 style = 'text-align: center; color: red;'>Avg of % Delay</h4>", unsafe_allow_html= True)
                st.markdown(f"<h3 style = 'text-align: center; color: blue;'>{Percent_Delays} %</h3>", unsafe_allow_html= True)
                with st.expander("% Delay Formula"):
                    st.latex(r'''
                    =\left(\frac{Σ Delayed Orders}{Σ OrdersPlaced}\right) * 100
                    ''')
            
            col1, col2  = st.columns(2)
            with col1 :
                st.plotly_chart(vizHelper.area_chart(percent_dr_vendor_score_df, 'Month', 'Vendor Score','Month', 'Vendor Score', 'Month Wise Avg of Vendor Score'))
            with col2: 
                import plotly.graph_objects as go

                fig = go.Figure(go.Indicator(
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    value = avg_vendor_score,
                    mode = "gauge+number+delta",
                    title = {'text': "Avg Vendor Score"},
                    delta = {'reference': avg_vendor_score_all},
                    gauge = {'axis': {'range': [0, 5]},
                            'bar': {'color': "darkblue"},
                            'steps' : [
                                {'range': [0, 3], 'color': "red"},
                                {'range': [3, 4], 'color': "yellow"},
                                {'range': [4, 5], 'color': "green"}],
                            'threshold' : {'line': {'color': "blue", 'width': 4}, 'thickness': 0.75, 'value': avg_vendor_score}}))
                fig.update_layout(autosize=False,width=600,height=500)
                st.plotly_chart(fig)
            

            col1, col2 = st.columns(2)

            avg_vend = purch.groupby(by = 'Vendor Name').mean().reset_index()[['Vendor Name', 'Vendor Score']]
            best = avg_vend.sort_values(by='Vendor Score', ascending=False).head(10)
            worst = avg_vend[avg_vend["Vendor Score"] < 5].head(10).sort_values(by="Vendor Score", ascending=False)
            col1.plotly_chart(vizHelper.barchart(best,'Vendor Score', 'Vendor Name',title = 'Best Performers', orientation='h'))
            col2.plotly_chart(vizHelper.barchart(worst,'Vendor Score', 'Vendor Name',title = 'Worst Performers', orientation='h'))
            st.subheader("Complete Data")
            AgGrid(purch)
            #AgGrid(data = purch, height = 20)
            st.download_button(
            '📥 Download Dataset',
            purch.to_csv( index = False ).encode('utf-8'),
            "VendorAnalysisData.csv",
            "text/csv",
            key='download-csv'
            )
            #userManagement.app_logger(username, "Vendor Analysis")


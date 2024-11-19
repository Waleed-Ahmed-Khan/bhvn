import streamlit as st 
import pandas as pd 

@st.cache(suppress_st_warning=True, allow_output_mutation=True, ttl = 800)
def preprocess_packing(complete_df, start_date, end_date, year, po_selection, customer_selection, overtime_selection, mastercode_selection, size_selection):
    
    mask =  (complete_df['date'].astype('datetime64').dt.date.between(start_date, end_date)) & (complete_df['year'] == year) & (complete_df['customer_PO'].isin(po_selection)) & (complete_df['SubCategory'].isin(customer_selection)) & (complete_df['overtime'].isin(overtime_selection)) & (complete_df['mastercode'].isin(mastercode_selection)) & (complete_df['size'].isin(size_selection))
    complete_df = complete_df[mask]
    complete_df = complete_df.dropna(subset = ['mastercode', 'size']) #adding mastercode == nan will increase the number of co

    #targets = complete_df['h_target'].values
    complete_df["h_target"] = complete_df["h_target"].apply(lambda x : 5550 if x == 0 else x) 
    complete_df["h_target"] = complete_df["h_target"] * 15
    #complete_df = complete_df[pd.notna(complete_df['mastercode'])]
    total_output = complete_df['qty'].sum()
    total_target = complete_df['target'].sum()
    total_co = complete_df['C/O'].sum()
    
    total_percent_co = (total_co/len(complete_df['C/O']))*100
    avg_efficiency = (complete_df["% Eff"].mean())*100
    avg_throughput = complete_df['Hourly Throughput'].mean()
    complete_df["% Eff"]  = (complete_df['% Eff'])*100

    sorted_months = complete_df.groupby(by='Month', as_index=False)['month_no'].first()
    
    co_by_month = complete_df.groupby(by='Month', as_index=False)['C/O'].sum()
    executions_by_month = complete_df.groupby(by='Month', as_index=False)['C/O'].count().rename(columns={'C/O':'count_co'})
    co_exe_by_month = pd.merge(left=co_by_month, right=executions_by_month, on='Month', how='left')
    co_exe_by_month['percent_co'] = (co_exe_by_month['C/O']/co_exe_by_month['count_co'])*100
    co_exe_by_month = co_exe_by_month.drop(columns=['C/O', 'count_co'])
    co_exe_by_month = pd.merge(left=co_exe_by_month, right=sorted_months, how='left').sort_values(by='month_no', ascending= True).drop(columns=['month_no'])
    eff_by_month = complete_df.groupby(by='Month', as_index=False)['% Eff'].mean()
    eff_by_month = pd.merge(left=eff_by_month, right=sorted_months, how='left').sort_values(by='month_no', ascending=True).drop(columns=['month_no'])
    eff_by_month['% Eff'] = eff_by_month['% Eff']
    throughput_by_month = complete_df.groupby(by='Month', as_index=False)['Hourly Throughput'].mean()
    throughput_by_month = pd.merge(left=throughput_by_month, right=sorted_months, how='left').sort_values(by='month_no', ascending=True).drop(columns=['month_no'])
    
    customer_wise_throughput = complete_df.groupby('SubCategory', as_index=False)['Hourly Throughput'].mean()
    customer_wise_eff = complete_df.groupby('SubCategory', as_index=False)['% Eff'].mean()
    customer_wise_eff_thr = pd.merge(left=customer_wise_throughput, right=customer_wise_eff, how='left').sort_values(by='% Eff', ascending = False)
    #line_wise_throughput = complete_df.groupby('line_number', as_index=False)['Hourly Throughput'].mean()
    #line_wise_eff = complete_df.groupby('line_number', as_index=False)['% Eff'].mean()
    #line_wise_eff_thr = pd.merge(left=line_wise_throughput, right=line_wise_eff, how='left').sort_values(by='% Eff', ascending = False)
    
    customer_qty = complete_df.groupby(by='SubCategory', as_index=False)['qty'].sum().rename(columns={'SubCategory':'Customer Name', 'qty': 'Quantity'})
    
    co_by_brand = complete_df.groupby(by='SubCategory', as_index=False)['C/O'].sum()
    #co_by_line = complete_df.groupby(by='line_number', as_index=False)['C/O'].sum()
    return complete_df, total_output, total_target, total_co, total_percent_co, avg_efficiency, avg_throughput , sorted_months, co_exe_by_month,eff_by_month, throughput_by_month, customer_wise_eff_thr, customer_qty, co_by_brand

@st.cache(suppress_st_warning=True, allow_output_mutation=True, ttl = 500)
def preprocess_packing_lastworking(complete_df):
    total_output = complete_df['qty'].sum()
    total_target = complete_df['target'].sum()
    total_co = complete_df['C/O'].sum()
    
    total_percent_co = (total_co/len(complete_df['C/O']))*100
    avg_efficiency = (complete_df["% Eff"].mean())*100
    avg_throughput = complete_df['Hourly Throughput'].mean()
    complete_df["% Eff"]  = (complete_df['% Eff'])*100

    sorted_months = complete_df.groupby(by='Month', as_index=False)['month_no'].first()
    
    co_by_month = complete_df.groupby(by='Month', as_index=False)['C/O'].sum()
    executions_by_month = complete_df.groupby(by='Month', as_index=False)['C/O'].count().rename(columns={'C/O':'count_co'})
    co_exe_by_month = pd.merge(left=co_by_month, right=executions_by_month, on='Month', how='left')
    co_exe_by_month['percent_co'] = (co_exe_by_month['C/O']/co_exe_by_month['count_co'])*100
    co_exe_by_month = co_exe_by_month.drop(columns=['C/O', 'count_co'])
    co_exe_by_month = pd.merge(left=co_exe_by_month, right=sorted_months, how='left').sort_values(by='month_no', ascending= True).drop(columns=['month_no'])
    eff_by_month = complete_df.groupby(by='Month', as_index=False)['% Eff'].mean()
    eff_by_month = pd.merge(left=eff_by_month, right=sorted_months, how='left').sort_values(by='month_no', ascending=True).drop(columns=['month_no'])
    eff_by_month['% Eff'] = eff_by_month['% Eff'] *100
    throughput_by_month = complete_df.groupby(by='Month', as_index=False)['Hourly Throughput'].mean()
    throughput_by_month = pd.merge(left=throughput_by_month, right=sorted_months, how='left').sort_values(by='month_no', ascending=True).drop(columns=['month_no'])
    
    customer_wise_throughput = complete_df.groupby('SubCategory', as_index=False)['Hourly Throughput'].mean()
    customer_wise_eff = complete_df.groupby('SubCategory', as_index=False)['% Eff'].mean()
    customer_wise_eff_thr = pd.merge(left=customer_wise_throughput, right=customer_wise_eff, how='left').sort_values(by='% Eff', ascending = False)
    #line_wise_throughput = complete_df.groupby('line_number', as_index=False)['Hourly Throughput'].mean()
    #line_wise_eff = complete_df.groupby('line_number', as_index=False)['% Eff'].mean()
    #line_wise_eff_thr = pd.merge(left=line_wise_throughput, right=line_wise_eff, how='left').sort_values(by='% Eff', ascending = False)
    
    customer_qty = complete_df.groupby(by='SubCategory', as_index=False)['qty'].sum().rename(columns={'SubCategory':'Customer Name', 'qty': 'Quantity'})
    
    co_by_brand = complete_df.groupby(by='SubCategory', as_index=False)['C/O'].sum()
    #co_by_line = complete_df.groupby(by='line_number', as_index=False)['C/O'].sum()
    #co_by_line = co_by_line[co_by_line['C/O'] != 0]

    planned_vs_target = complete_df.groupby('mastercode', as_index=False)[['qty','target']].sum().rename(columns={'qty':'Output', 'target':'Target'}).astype({'Output':int, 'Target': int})
    
    return complete_df, total_output, total_target, total_co, total_percent_co, avg_efficiency, avg_throughput , sorted_months, executions_by_month ,eff_by_month, throughput_by_month, customer_wise_eff_thr, customer_qty, co_by_brand, planned_vs_target 
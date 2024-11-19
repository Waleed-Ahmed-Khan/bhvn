#import pandas as pd 
import streamlit as st
#from help import helper
#import numpy as np
#import plotly.graph_objects as go
#import calendar
import static.formatHelper as fh
from streamlit_option_menu import option_menu
#from datetime import datetime
from salesPckg.sales_main import render_sales_form, render_sales_operations_l, render_sales_opreations
from salesPckg.sales_tabs import render_sales_tabs

def render_sales(username):
    
    st.write('<style>div.row-widget.stButton > div{flex-direction:row;} </style>', unsafe_allow_html=True)
    st.write('<style>div.st-bf{flex-direction:column;} div.st-ag{font-weight:bold;padding-left:2px;}</style>', unsafe_allow_html=True)
    st.write(fh.format_st_button(), unsafe_allow_html=True)

    selection = option_menu(

                menu_title = "Sales & Logistics Department",
                options = ["Sales Dashboard", "Sales Legacy", "Logistics Dashboard", "Last Working Day","Data Entry"],
                icons = ["file-earmark-bar-graph-fill","cloud-haze2","truck", "alarm-fill", "card-checklist"],
                menu_icon = ["briefcase-fill"],
                orientation = "horizontal"
    )

    try:
        if selection == 'Sales Dashboard' :
            render_sales_tabs(username)
            #render_sales_opreations(username)

        elif selection == 'Sales Legacy' :
            render_sales_operations_l(username)
        elif selection == 'Logistics Dashboard':
            st.header("Coming Soon ... ⏳")
        elif selection == 'Last Working Day':
            st.header("Coming Soon ... ⏳")
        elif selection == 'Data Entry':
            render_sales_form(username)
    except Exception as e:
        #st.error(f"Dear {str.title(username)}, Something went wrong. Please contact admin in case the problem persists. We are sorry 😌")
        raise (e)
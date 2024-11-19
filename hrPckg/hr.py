#import pandas as pd 
import streamlit as st
#from help import helper
#import numpy as np
#import plotly.graph_objects as go
#import calendar
import static.formatHelper as fh
from streamlit_option_menu import option_menu
#from datetime import datetim\
from hrPckg.hr_main import RenderHR
from hrPckg.hr_tabs import render_hr_tabs

def render_hr(username):
    hr_ops = RenderHR()
    st.write('<style>div.row-widget.stButton > div{flex-direction:row;} </style>', unsafe_allow_html=True)
    st.write('<style>div.st-bf{flex-direction:column;} div.st-ag{font-weight:bold;padding-left:2px;}</style>', unsafe_allow_html=True)
    st.write(fh.format_st_button(), unsafe_allow_html=True)

    selection = option_menu(

                menu_title = "Human Resource Department",
                options = ["HR Dashboards", "Today's Attendance", "Employee Health Analysis", "Data Entry"],
                icons = ["person-bounding-box", "alarm-fill", "bandaid", "card-checklist"],
                menu_icon = ["people-fill"],
                orientation = "horizontal"
    )

    try:
        if selection == 'HR Dashboards' :
            render_hr_tabs(username)
            #render_sales_opreations(username)
        elif selection == 'Employee Health Analysis':
            hr_ops.render_medical_analysis(username)
        elif selection == "Today's Attendance":
            hr_ops.render_hr_lw(username)
        elif selection == 'Data Entry':
            #render_sales_form(username)
            pass
    except Exception as e:
        #st.error(f"Dear {str.title(username)}, Something went wrong. Please contact admin in case the problem persists. We are sorry 😌")
        raise (e)
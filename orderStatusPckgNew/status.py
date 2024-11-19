from pathlib import Path
import sys
FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]  # YOLOv5 root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

import streamlit as st
import static.formatHelper as fh
from streamlit_option_menu import option_menu
#from datetime import datetime
#from orderStatusPckgNew.status_main import render_overall_status
from orderStatusPckgNew.status_sewing import render_sewing_status
from orderStatusPckgNew.status_auto import render_auto_status
from orderStatusPckgNew.status_packing import render_packing_status
from orderStatusPckgNew.status_cutting import render_cutting_status
from orderStatusPckgNew.status_printing import render_printing_status
from orderStatusPckgNew.status_issuance import render_issuance_status
from orderStatusPckgNew.status_final_inspection import render_final_inspection_status
from orderStatusPckgNew.status_purchase import render_purchase_status
from orderStatusPckgNew.status_tabs import render_status_tabs

def render_order_status(username):
    
    st.write('<style>div.row-widget.stButton > div{flex-direction:row;} </style>', unsafe_allow_html=True)
    st.write('<style>div.st-bf{flex-direction:column;} div.st-ag{font-weight:bold;padding-left:2px;}</style>', unsafe_allow_html=True)
    st.write(fh.format_st_button(), unsafe_allow_html=True)

    selection = option_menu(

                menu_title = "Real Time Orders Tracking",
                options = ['Overall Status','Sales','Purchase', 'Cutting', 'Printing', 'Automation','Issuance', 'Sewing','Final Inspection', 'Packing'],
                icons = ["hourglass-split","briefcase-fill","wallet2", "scissors", "palette2", "gear-wide-connected", "bag-check-fill", "collection-fill", "clipboard-check", "box-seam"],
                menu_icon = ["calendar2-week-fill"],
                orientation = "horizontal"
    )
    
    try:
        if selection == 'Overall Status' :
            try:
                render_status_tabs(username)
            except Exception as e:
                raise e
                #st.error(f"Dear {username}, something went wrong at overall status entry. Contact Admin if the problem persists, we are sorry 😟")
        elif selection == 'Sales':
            st.header("Coming Soon ... ⏳")
        elif selection == 'Purchase':
            render_purchase_status(username)
        elif selection == 'Cutting':
            try:
                render_cutting_status(username)
            except:
                st.error(f"Dear {username}, something went wrong at Cutting status entry. Contact Admin if the problem persists, we are sorry 😟")
        elif selection == 'Printing':
            try:
                render_printing_status(username)
            except:
                st.error(f"Dear {username}, something went wrong at Printing status entry. Contact Admin if the problem persists, we are sorry 😟")
        elif selection == 'Automation':
            try:
                render_auto_status(username)
            except:
                st.error(f"Dear {username}, something went wrong at Automation status entry. Contact Admin if the problem persists, we are sorry 😟")
        
        elif selection == 'Issuance':
            try:
                render_issuance_status(username)
            except:
                st.error(f"Dear {username}, something went wrong at Issuance status entry. Contact Admin if the problem persists, we are sorry 😟")

        elif selection == 'Sewing':
            try:
                render_sewing_status(username)
            except:
                st.error(f"Dear {username}, something went wrong at Sewing status entry. Contact Admin if the problem persists, we are sorry 😟")    
        elif selection == 'Final Inspection':
            try:
                render_final_inspection_status(username)
            except:
                st.error(f"Dear {username}, something went wrong at Final Inspection entry. Contact Admin if the problem persists, we are sorry 😟")
        
        elif selection == 'Packing':
            try:
                render_packing_status(username)
            except:
                st.error(f"Dear {username}, something went wrong at Packing status entry. Contact Admin if the problem persists, we are sorry 😟") 

    except Exception as e:
        #st.error(f"Dear {str.title(username)}, Something went wrong. Please contact admin in case the problem persists. We are sorry 😌")
        raise (e)

if __name__ == '__main__':
    render_order_status("hasnain")
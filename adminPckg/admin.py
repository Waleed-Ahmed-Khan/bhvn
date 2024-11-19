import streamlit as st
import static.formatHelper as fh
from streamlit_option_menu import option_menu
from adminPckg import admin_main

def render_admin(username):
    st.write('<style>div.row-widget.stButton > div{flex-direction:row;} </style>', unsafe_allow_html=True)
    st.write('<style>div.st-bf{flex-direction:column;} div.st-ag{font-weight:bold;padding-left:2px;}</style>', unsafe_allow_html=True)
    st.write(fh.format_st_button(), unsafe_allow_html=True)

    selection = option_menu(

                menu_title = "Admin",
                options = ['User Dashboard', 'Create New User', 'Update User','Delete User', 'Update Customers', 'Update Designations', 'Update Rights'],
                icons = ["bar-chart-fill", "person-plus-fill", "people","person-x-fill", "bounding-box", "briefcase", "check2-square"],
                menu_icon = ["person-workspace"],
                orientation = "horizontal"
    )

    try:
        if selection == 'User Dashboard':
            admin_main.render_usersDashboard(username)
        #elif st.session_state['new_user']:
        elif selection == 'Create New User':
            admin_main.renderCreateNewUser(username)
        
        elif selection == 'Update User':
            admin_main.renderUpdateUser(username)
        elif selection == 'Delete User':
            admin_main.renderDeleteUser(username)
        elif selection == 'Update Customers':
            admin_main.renderUpdateCustomers(username)
        elif selection == 'Update Designations':
            admin_main.renderUpdateDesignations(username)
        elif selection == 'Update Rights':
            admin_main.renderUpdateUserRightsPool(username)
    except Exception as e:
        raise e
        #st.info("That didn't go well, don't worry, hit me again!☝️")
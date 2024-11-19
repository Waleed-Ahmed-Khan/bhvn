
import streamlit as st
from static.formatHelper import tabs_font_size
from orderStatusPckgNew.status_main import render_overall_status_transactions, render_overall_status_strategic
#st.write(font_css, unsafe_allow_html=True)
def render_status_tabs(username):
    whitespace = 14
    st.write(tabs_font_size(), unsafe_allow_html=True)
    listTabs = ["📊Order Status", "📈Lead-time Analysis"]
    tab1, tab2 = st.tabs([s.center(whitespace,"\u2001") for s in listTabs])

    with tab1:
        #st.header("Transactional Status")
        render_overall_status_transactions(username)
        
    with tab2:
        #st.header("Strategic Analysis")
        render_overall_status_strategic(username)

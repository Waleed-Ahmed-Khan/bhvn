from salesPckg.sales_main import render_sales_opreations, render_sales_transaction, render_last_invoice
import streamlit as st
from static.formatHelper import tabs_font_size
#st.write(font_css, unsafe_allow_html=True)
def render_sales_tabs(username):
    whitespace = 14
    st.write(tabs_font_size(), unsafe_allow_html=True)
    listTabs = ["🔃Transactional Dashboard", "📊Operational Dashboard", "🕖Last Invoice", "📈Strategic Dashboard"]
    tab1, tab2, tab3, tab4 = st.tabs([s.center(whitespace,"\u2001") for s in listTabs])

    with tab1:
        st.header("Transactional Dashboard")
        render_sales_transaction(username)
    with tab2:
        st.header("Operational Dashboard")
        render_sales_opreations(username)

    with tab3:
        render_last_invoice(username)
        
    with tab4:
        st.header("Strategic Dashboard")
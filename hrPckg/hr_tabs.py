from hrPckg.hr_main import RenderHR
import streamlit as st
from static.formatHelper import tabs_font_size
from hrPckg import emp_id_real_time
#st.write(font_css, unsafe_allow_html=True)
def render_hr_tabs(username):
    hr_instance = RenderHR()
    whitespace = 14
    st.write(tabs_font_size(), unsafe_allow_html=True)
    listTabs = ["📈Operational Dashboard", "👨🏻Employee Profile", "🛃Absenteeism Analysis", "📊Stay Duration", "📷Real-time Employee ID"]
    tab1, tab2, tab3, tab4, tab5 = st.tabs([s.center(whitespace,"\u2001") for s in listTabs])

    with tab1:
        st.header("Operational Dashboard")
        hr_instance.render_hr_operations(username)
        
    with tab2:
        st.header("Employee Profile")
        hr_instance.render_performance_report(username)
    with tab3:
        st.header("Absenteeism Analysis")
        hr_instance.render_abs_analysis(username)
        
    with tab4:
        st.header("Stay Duration Analysis") 
        hr_instance.render_stay_duration(username)
    
    with tab5:
        emp_id_real_time.render_realtime(username)

    return hr_instance
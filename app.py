import streamlit as st
from PIL import Image
from datetime import date
import json
from streamlit_lottie import st_lottie
import accountsPckg.costing.costing as costing
import adminPckg.userManagement as userManagement, purchasePckg.purchase as purchase
import cutting, sewingPckg.sewing as sewing, adminPckg.usersDashboard as usersDashboard
import printingPckg.printing as printing
import tprsPckg.tprs as tprs
import packingPckg.packing as packing

#import eda
import AutoPckg.auto as auto
import adminPckg.admin as admin
from orderStatusPckgNew.status import render_order_status
from salesPckg.sales import render_sales
import hrPckg.hr as hr
import streamlit_authenticator as stauth
from common.sqlDBOperations import sqlDBManagement
import common.helper as helper

def main(username, name, authenticator):
    try:
        @st.cache(suppress_st_warning=True, show_spinner=False)
        def the_engine_on_request(files :list):
            with open (files[0], "r") as f:
                hello = json.load(f)
            with open (files[1], "r") as f:
                data_analysis = json.load(f)
            return hello, data_analysis
        if "load_state" not in st.session_state :
            from static.formatHelper import tabs_font_size
            st.write(tabs_font_size(), unsafe_allow_html=True)
            with st.spinner("Sit tight, we are getting things ready for you... 🏋️‍♂️⏳🚀"):
                hello , data_analysis = the_engine_on_request(["static/hello.json", "static/data_analysis.json"])
            #= load_lottiefile()
            col1, col2 = st.columns(2)
            with col1:
                st_lottie(hello, 
                        #speed=0.1,
                        #reverse=True,
                        #loop=True,
                        #quality = "hight",
                        #height = 1000,
                        #width = 500,
                        #key=None
                            )
            with col2:
                st_lottie(data_analysis)
            st.session_state.load_state = True
        #if st.session_state.load_state:
        #st.session_state.load_state=True
        st.sidebar.title("BHVN BI Application")
        # if "login_session" not in st.session_state:
        #     username= st.sidebar.text_input('Username')
        #     username = username.lower()
        #     password = st.sidebar.text_input("Password", type = 'password')
        #     st.session_state['username'] = username
        #     st.session_state['password'] = password
        #if st.sidebar.checkbox('Login'):
        task = userManagement.user_entry(username, name, authenticator)
        st.session_state["login_session"] = True

        if task == "Orders Tracking":
            render_order_status(username)
        elif task == "Sales":
            render_sales(username)
        elif task == "HR":
            hr.render_hr(username)
        elif task == "Accounts & Finance":
            costing.render_finance(username)
        elif task == "Purchase":
            try:
                purchase.render_purchase(username)
            except Exception as e:
                raise e
                st.write('System ran into errors while performing purchase calculations. Please check your selections make the request again! If you could not resolve the problem then feel free to send an email at "hasnain@bhgloves.com", Thank you!')
        elif task == "Cutting":
            #try:
            cutting.render_cutting(username)
            #usersDashboard.render_rightsManagement()
            #except:
                #st.write('System ran into errors while performing Cutting calculations. Please check your selections make the request again! If you could not resolve the problem then feel free to send an email at "hasnain@bhgloves.com", Thank you!')
        elif task == 'Printing':
                printing.render_printing(username)
        elif task == 'TPR':
                tprs.render_tprs(username)
        elif task == 'Automation':
                auto.render_auto(username)
        elif task == 'Sewing':
            #try:
            sewing.render_sewing(username)
            #except:
            #    st.error('System ran into errors while performing sewing calculations. Please check your selections make the request again! If you could not resolve the problem then feel free to send an email at "hasnain@bhgloves.com", Thank you!')
        elif task == 'Packing':
            packing.render_packing(username)

        elif task == 'Admin':
            admin.render_admin(username)
        elif task == 'Update Password':
            userManagement.update_password(username)
        elif task == 'Delete User':
            userManagement.del_user()
        elif task == 'Rights Management':
            usersDashboard.render_rightsManagement()
        # elif task == 'EDA':
        #     eda.render_eda(username)
    except Exception as e:
        pass
        #raise(e)
if __name__ == '__main__':
    st.set_page_config(
    page_title="BHVN BI Application",
    page_icon="static/bhvnLogo.png",
    layout="wide",
    initial_sidebar_state="expanded",)
    hide_streamlit_style = """
                <style>
                div.block-container{padding-top:1rem;}
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                footer {
                    
                visibility: hidden;
                
                }
                footer:after {
                    content:'Copyright © 2021-2023 BHVN'; 
                    visibility: visible;
                    display: block;
                    position: relative;
                    #background-color: red;
                    padding: 5px;
                    top: 2px;
                }
                </style>
                """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    if "all_users" not in st.session_state:
        bhvnMysql = sqlDBManagement(host = helper.OLAP_HOST, username = helper.OLAP_USER_NAME,
                                password = helper.SQL_DWH_PASS, database = helper.OLAP_DB_NAME)
        all_users =  bhvnMysql.getDataFramebyQuery(f"SELECT username, name, email, designation, customer, rights, password from tblusers")
        #= all_users['password'].apply(lambda x:x.split("'")[1])
        #all_users['password'] = [pwd.split("'")[1] if len(pwd)==3 else pwd for pwd in all_users['password']]
        #print(all_users)
        st.session_state["all_users"] = all_users
        auth_table = all_users[['username', 'name', 'password']]
        #auth_table.rename(columns={'username':'usernames'}, inplace=True)
        auth_dict = auth_table.set_index('username').T.to_dict()
        auth_dict_credentials = dict()
        auth_dict_credentials["usernames"] = auth_dict
        st.session_state["auth_dict_credentials"] = auth_dict_credentials
    authenticator = stauth.Authenticate(st.session_state["auth_dict_credentials"],
                                        "bhvnbiapplication", "48ht75tgh7r5ht84h83hf489h93hf47hg57hg84fh93", cookie_expiry_days = 30)
    name, authentication_status, username = authenticator.login("BHVN-BI-Login", "sidebar")

    if authentication_status == False:
        st.sidebar.error("Username/password is incorrect")
    #if "login_attempt" in st.session_state:
    if authentication_status == None:
        st.sidebar.warning("Please enter your username and password")
        #st.session_state["login_attempt"] =True


    if authentication_status:
    
        image = Image.open("static/bhvnLogo.png")
        st.sidebar.image(image,
            caption=f"Copyright © 2021-{date.today().year} BHVN",
            use_column_width=True)
            
        main(username, name, authenticator)
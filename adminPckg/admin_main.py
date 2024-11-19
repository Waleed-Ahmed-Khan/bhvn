from common import helper, vizHelper
import streamlit as st
import adminPckg.userManagement as userManagement
import static.formatHelper as fh
import pandas as pd
from st_aggrid import AgGrid
from static.formatHelper import hover_size
import adminPckg.admin_helper as admin_helper
from common.sqlDBOperations import sqlDBManagement
import re
import streamlit_authenticator as stauth
import appConfig as CONFIG
#bhvnMysql = mysqlDBManagement(host = helper.OLAP_HOST, username = helper.OLAP_USER_NAME,
#                            password = helper.SQL_DWH_PASS, database = helper.OLAP_DB_NAME)

def render_usersDashboard(username):
    if CONFIG.BHVN_CENT_DB_SESSION not in st.session_state:
        st.session_state[CONFIG.BHVN_CENT_DB_SESSION] = sqlDBManagement(host = helper.DB_CENT_HOST, username = helper.DB_CENT_USR,
                            password = helper.DB_CENT_PASS, database = helper.DB_CENT_NAME)
    st.markdown(hover_size(), unsafe_allow_html=True)
    st.subheader('User Activity Logs')
    #cursor_sql_olap , conn_sql_olap = helper.connect_sql_olap()
    if CONFIG.USER_LOGS_SESSION not in st.session_state:
        user_logs = st.session_state[CONFIG.BHVN_CENT_DB_SESSION].getDataFramebyQuery("SELECT * FROM userlogs;")
        st.session_state[CONFIG.USER_LOGS_SESSION] = user_logs 
    else:
        user_logs= st.session_state[CONFIG.USER_LOGS_SESSION]
    user_logs = helper.get_user_logs(user_logs)
    
    active_users = st.session_state['all_users']['username'].tolist()
    active_users.remove('gadmin')
    user_logs =  user_logs[user_logs['UserName'].isin(active_users)]
    user_logs['date_filter'] = user_logs['DateTimeUTC'].astype('datetime64').dt.strftime("%Y/%m/%d")
    date = user_logs['date_filter'].unique().tolist()
    all_users = user_logs['UserName'].unique().tolist()
    all_users.insert(0, 'All Users') 
    col1, col2, col3 =  st.columns(3)
    with col1:
        st.markdown("**Start Date :**")
        start_date = st.date_input('', pd.to_datetime(min(date)))
    with col2:
        st.markdown("**End Date :**")
        end_date = st.date_input('', pd.to_datetime(max(date)))
    with col3:
        st.markdown("**User Name :**")
        user_selection = st.multiselect('',  all_users, default='All Users')
    st.markdown('<hr/>', unsafe_allow_html = True)
    if st.button("📈 Let's Go!"):
        st.markdown('<hr/>', unsafe_allow_html = True)
        if user_selection ==["All Users"]:
            user_selection = all_users
        mask = (user_logs['date_filter'].astype('datetime64').dt.date.between(start_date, end_date)) & (user_logs['UserName'].isin(user_selection))
        user_logs = user_logs[mask]
        col1, col2 = st.columns(2)
        with col1 :
            fig = vizHelper.heatmap(user_logs, 'Day', 'Month','activity_count', 'count', 'Month', 'Day', 'Total visits', 'Daily User visits over the months')
            st.plotly_chart(fig)
        with col2 :
            fig = vizHelper.heatmap(user_logs, 'Day','Activity', 'activity_count', 'count', 'Departments',  'Day','Total visits', 'Daily, Department wise user activity')
            st.plotly_chart(fig)
        col1, col2 = st.columns(2)
        st.markdown('<hr/>', unsafe_allow_html = True)
        with col1:
            user_logs_groupby = user_logs.groupby(by='Activity', as_index=False)['activity_count'].sum().sort_values(by='activity_count', ascending=True)
            fig = vizHelper.barchart(user_logs_groupby,'activity_count', 'Activity', title='Total Activities')
            st.plotly_chart(fig)
        with col2:
            user_logs_groupby = user_logs.groupby(by='UserName', as_index=False)['activity_count'].sum().sort_values(by='activity_count', ascending=True)
            fig = vizHelper.barchart(user_logs_groupby,'activity_count', 'UserName', title='Total Visits by User')
            st.plotly_chart(fig)
        col1, col2 = st.columns(2)
        st.markdown('<hr/>', unsafe_allow_html = True)
        with col1:
            fig = vizHelper.heatmap(user_logs, 'Day', 'UserName','activity_count', 'count', 'Month', 'Day', 'Total visits', 'Daily User visits')
            st.plotly_chart(fig)
        with col2:
            fig = vizHelper.heatmap(user_logs, 'Activity','UserName', 'activity_count', 'count', 'Departments',  'Day','Total visits', 'Daily, Department wise user activity')
            st.plotly_chart(fig)
        st.subheader("User Profiles")
        user_profiles = st.session_state['all_users']
        user_profiles = user_profiles[user_profiles['username']!='gadmin']
        AgGrid(user_profiles.drop(columns=['password']))
        st.markdown('<hr/>', unsafe_allow_html = True)
        st.subheader('Download Activity Logs')
        user_logs_disp = user_logs.drop(columns=['Month Number', 'Month', 'Day Number', 'Day', 'activity_count', 'date_filter']) 
        user_logs = user_logs.drop(columns=['Month Number', 'Month', 'Day Number', 'Day', 'activity_count', 'date_filter']) 
        AgGrid(user_logs_disp)
        df_xlsx = helper.to_excel(user_logs)
        st.download_button(label='📥 Download User Logs',
                            data=df_xlsx ,
                            file_name= 'UserLogs.xlsx')
        userManagement.app_logger(username, "User Profiles")
def renderCreateNewUser(username):
    #all_rights_df = 
    with st.form(key='add-new-user'):
        if "bhvnMysql" not in st.session_state:
            st.session_state["bhvnMysql"] = sqlDBManagement(host = helper.OLAP_HOST, username = helper.OLAP_USER_NAME,
                                password = helper.SQL_DWH_PASS, database = helper.OLAP_DB_NAME)
        rights_list = st.session_state["bhvnMysql"].getDataFramebyQuery("SELECT rights from allrights;")
        designation_list = st.session_state["bhvnMysql"].getDataFramebyQuery("SELECT designation from tbldesignations;")
        customer_list = st.session_state["bhvnMysql"].getDataFramebyQuery("SELECT customer from tblcustomers;")
        st.header("Create New User Account")
        col1, col2, col3 = st.columns(3)
        with col1:
            new_username = st.text_input("Username")
        with col2:
            full_name = st.text_input("Full Name")
        with col3:
            user_email = st.text_input("Email Address")
        col1, col2 = st.columns(2)
        with col1:
            new_password = st.text_input("Password", type = 'password')
        with col2:
            rights = st.multiselect("Assign Rights", rights_list)
        col1, col2 = st.columns(2)
        with col1:
            new_designation = st.selectbox("Designation", designation_list)
        with col2:
            new_customer = st.selectbox("Customer Name", customer_list)
        submit_new_user_form = st.form_submit_button(label = '💼SignUp')

    #rights = ','.join([i for i in  rights])
    #st.markdown(f"Rights Assigned : {rights}")
    if submit_new_user_form:
        try:
            hashed = stauth.Hasher([new_password]).generate()[0]
            #hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            query = f'''INSERT INTO tblusers(username,name, pwd,password,rights,designation,customer, email)
                     VALUES ("{new_username}","{full_name}", "{new_password}", "{hashed}",
                             "{rights}", "{new_designation}", "{new_customer}", "{user_email}")'''
            st.session_state["bhvnMysql"].executeOperation(query=query)
            #helper.add_userdata(new_username.lower(), helper.make_hashes(new_password), rights)
            st.success(f'Dear {username}, a new user with the usrename "{new_username}" has been created in the system.')
            st.info("Please provide these login credentials along with the URL to the new user.")
            userManagement.app_logger(username, f"New User Account {new_username}")
            st.balloons()
        except:
            st.error(f'User with the username "{new_username}" already exists, kindly provide another username.')
def renderUpdateUser(username):
    rights_list = st.session_state["bhvnMysql"].getDataFramebyQuery("SELECT rights from allrights;")
    designation_list = st.session_state["bhvnMysql"].getDataFramebyQuery("SELECT designation FROM tbldesignations;")
    designation_list = designation_list['designation'].tolist()
    customer_list = st.session_state["bhvnMysql"].getDataFramebyQuery("SELECT customer FROM tblcustomers;")
    customer_list = customer_list['customer'].tolist()
    users_list = st.session_state["bhvnMysql"].getDataFramebyQuery('SELECT username FROM tblusers WHERE username != "gadmin";')
    st.header("Update User Account")
    col1, col2, col3 = st.columns(3)
    with col1:
        username_selection = st.selectbox("Username", users_list)
    with col2:
        complete_name  = st.session_state["bhvnMysql"].getDataFramebyQuery(f'SELECT name from tblusers WHERE username="{username_selection}"')
        complete_name = st.text_input("Complete Name", value = complete_name['name'][0])
    with col3:
            user_email  = st.session_state["bhvnMysql"].getDataFramebyQuery(f'SELECT email from tblusers WHERE username="{username_selection}"')
            user_email = st.text_input("Email Address", value =user_email['email'][0])
    col1, col2 = st.columns(2)
    with col1:
        password = st.text_input("Password", type = 'password', placeholder = "Enter a new password", value='')
        if len(password) == 0:
            password = st.session_state["bhvnMysql"].getDataFramebyQuery(f'SELECT pwd from tblusers WHERE username="{username_selection}"')
            password = password['pwd'][0]
    with col2:
        
        current_rights = st.session_state["bhvnMysql"].getDataFramebyQuery(f'SELECT rights from tblusers WHERE username="{username_selection}"') 
        current_rights = current_rights['rights'].tolist()[0]
        current_rights = [re.sub('[^A-Za-z0-9 &]+', '', right.strip()) for right in list(re.split(',', current_rights))]
        if current_rights != ['']:
            user_rights = st.multiselect('User Rights : ', rights_list, default=current_rights)
        else: 
            user_rights = st.multiselect('User Rights : ', rights_list)
        user_rights = ",".join([str(right) for right in user_rights])
    col1, col2 = st.columns(2)
    with col1:
        user_designation = st.session_state["bhvnMysql"].getDataFramebyQuery(f'SELECT designation FROM tblusers where username="{username_selection}"')
        user_designation = user_designation['designation'][0]
        default_ix = designation_list.index(user_designation)
        designation = st.selectbox("Designation", designation_list, index = default_ix)
    with col2:
        user_customer = st.session_state["bhvnMysql"].getDataFramebyQuery(f'SELECT customer FROM tblusers where username="{username_selection}"')
        user_customer = user_customer['customer'][0]
        default_ix = customer_list.index(user_customer)
        customer = st.selectbox("Customer Name", customer_list, index = default_ix)
    #if 'Admin' in user_rights:
    #    user_rights = rights_list
    if st.button('🔐Update User Account'):
        try:
            hashed = stauth.Hasher([password]).generate()[0]
            #hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            query = f'''UPDATE tblusers SET username="{username_selection}",name="{complete_name}", pwd="{password}",
                        password="{hashed}",rights="{user_rights}",designation="{designation}",customer="{customer}", email="{user_email}"
                        WHERE username="{username_selection}";
                     '''
            st.session_state["bhvnMysql"].executeOperation(query=query)
            #helper.add_userdata(new_username.lower(), helper.make_hashes(new_password), rights)
            st.success(f'Dear {str.title(username)}, the user data for usrename "{str.title(username_selection)}" has been updated in the system.')
            userManagement.app_logger(username, "User Update")
            st.balloons()
            
        except:
            st.error(f'Sorry {str.title(username)},We Cannot update the data at the moment. Please Contact Admin')
def renderDeleteUser(username):
    rights_list = st.session_state["bhvnMysql"].getDataFramebyQuery("SELECT rights from allrights;")
    designation_list = st.session_state["bhvnMysql"].getDataFramebyQuery("SELECT designation FROM tbldesignations;")
    designation_list = designation_list['designation'].tolist()
    customer_list = st.session_state["bhvnMysql"].getDataFramebyQuery("SELECT customer FROM tblcustomers;")
    customer_list = customer_list['customer'].tolist()
    users_list = st.session_state["bhvnMysql"].getDataFramebyQuery('SELECT username FROM tblusers WHERE username != "gadmin";')
    st.header("Delete a User Account")
    col1, col2 = st.columns(2)
    with col1:
        username_selection = st.selectbox("Username", users_list)
    with col2:
        complete_name  = st.session_state["bhvnMysql"].getDataFramebyQuery(f'SELECT name from tblusers WHERE username="{username_selection}"')
        complete_name = st.text_input("Complete Name", value = complete_name['name'][0])
    col1, col2 = st.columns(2)
    with col1:
        password = st.text_input("Password", type = 'password', placeholder = "Enter a new password", value='')
        if len(password) == 0:
            password = st.session_state["bhvnMysql"].getDataFramebyQuery(f'SELECT pwd from tblusers WHERE username="{username_selection}"')
            password = password['pwd'][0]
    with col2:
        current_rights = st.session_state["bhvnMysql"].getDataFramebyQuery(f'SELECT rights from tblusers WHERE username="{username_selection}"') 
        current_rights = current_rights['rights'].tolist()[0]
        current_rights = [re.sub('[^A-Za-z0-9 &]+', '', right.strip()) for right in list(re.split(',', current_rights))]
        if current_rights != ['']:
            user_rights = st.multiselect('User Rights : ', rights_list, default=current_rights)
        else: 
            user_rights = st.multiselect('User Rights : ', rights_list)
    col1, col2 = st.columns(2)
    with col1:
        user_designation = st.session_state["bhvnMysql"].getDataFramebyQuery(f'SELECT designation FROM tblusers where username="{username_selection}"')
        user_designation = user_designation['designation'][0]
        default_ix = designation_list.index(user_designation)
        designation = st.selectbox("Designation", designation_list, index = default_ix)
    with col2:
        user_customer = st.session_state["bhvnMysql"].getDataFramebyQuery(f'SELECT customer FROM tblusers where username="{username_selection}"')
        user_customer = user_customer['customer'][0]
        default_ix = customer_list.index(user_customer)
        customer = st.selectbox("Customer Name", customer_list, index = default_ix)
    if 'Admin' in user_rights:
        user_rights = rights_list
    st.info(f'Dear {str.title(username)}, user with the usrename "{username_selection}" will be permanently removed from the system, proceed with caution')
    if st.button('❌Delete User'):
        try:
            query = f'''DELETE FROM tblusers
                        WHERE username="{username_selection}";
                     '''
            st.session_state["bhvnMysql"].executeOperation(query=query)
            #helper.add_userdata(new_username.lower(), helper.make_hashes(new_password), rights)
            st.success(f'Dear {str.title(username)}, you have successfully removed "{(username_selection)}" from the system. Clicking again on the "❌Delete User" will remove the next user automatically.')
            userManagement.app_logger(username, "Delete User")
            st.balloons()
        except:
            st.error(f'Sorry {str.title(username)},We could not delete the user at the moment. Please Contact Admin')
def renderUpdateCustomers(username):
    st.write('<style>div.row-widget.stRadio > div{flex-direction:row;} </style>', unsafe_allow_html=True)
    st.write('<style>div.st-bf{flex-direction:column;} div.st-ag{font-weight:bold;padding-left:2px;}</style>', unsafe_allow_html=True)
    choose=st.radio("",("Add New Customer","Delete Customer"))
    if choose == "Add New Customer":
        admin_helper.add_customer()
    elif choose == "Delete Customer":
        admin_helper.delete_customer()
    else:
        st.error('Somthing went wrong regarding your selection')
def renderUpdateDesignations(username):
    st.write('<style>div.row-widget.stRadio > div{flex-direction:row;} </style>', unsafe_allow_html=True)
    st.write('<style>div.st-bf{flex-direction:column;} div.st-ag{font-weight:bold;padding-left:2px;}</style>', unsafe_allow_html=True)
    choose=st.radio("",("Add New Designation","Delete Designation"))
    if choose == "Add New Designation":
        admin_helper.add_designation()
    elif choose == "Delete Designation":
        admin_helper.delete_designation()
    else:
        st.error('Somthing went wrong regarding your selection')
def renderUpdateUserRightsPool(uername):
    st.write('<style>div.row-widget.stRadio > div{flex-direction:row;} </style>', unsafe_allow_html=True)
    st.write('<style>div.st-bf{flex-direction:column;} div.st-ag{font-weight:bold;padding-left:2px;}</style>', unsafe_allow_html=True)
    choose=st.radio("",("Add New Right","Delete Rights"))
    if choose == "Add New Right":
        admin_helper.add_rights()
    elif choose == "Delete Rights":
        admin_helper.delete_rights()
    else:
        st.error('Somthing went wrong regarding your selection')

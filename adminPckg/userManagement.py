from common import helper
from time import time
import streamlit as st
import pandas as pd 
import datetime , pytz
import re , time , sqlite3, socket, datetime, adminPckg.usersDashboard as usersDashboard, adminPckg.userManagement as userManagement
import static.formatHelper as fh
from streamlit_option_menu import option_menu
from common.sqlDBOperations import sqlDBManagement
import streamlit_authenticator as stauth
from common import pwdValidator
from emailPckg.passValidation import Security


def get_user_ip():
    #IPAddress = request.remote_addr
    host_name = socket.gethostname()    
    IPAddress = socket.gethostbyname(host_name)
    return IPAddress
'''
def get_add_ip():
    helper.create_ipTable()
    access_token = '2f7c537f04205f'
    handler = ipinfo.getHandler(access_token)
    details = handler.getDetails().all
    (IP, City, Region, CountryCode, Location,Organization, 
    PostalCode, TimeZone, CountryName, Latitude, Longitude)  = (details['ip'],details['city'],
                details['region'], details['country'], details['loc'], details['org'],
                details['postal'], details['timezone'], details['country_name'],
                details['latitude'],details['longitude'])
    helper.add_new_ip(IP,City, Region, CountryCode, Location, Organization, PostalCode, TimeZone, CountryName, Latitude, Longitude)
    #return IP, Hostname, Anycast, City, Region, CountryCode, Location,Organization, PostalCode, TimeZone, CountryName, Latitude, Longitude
#IP, Hostname, Anycast, City, Region, CountryCode, Location,Organization, PostalCode, TimeZone, CountryName, Latitude, Longitude = get_ip_data()
#helper.add_new_ip(IP, Hostname, Anycast, City, Region, CountryCode, Location,Organization, PostalCode, TimeZone, CountryName, Latitude, Longitude)
'''
def app_logger(username, activity):
        #helper.create_userlogsTable()
        utc_now = datetime.datetime.now(datetime.timezone.utc)
        local_now = datetime.datetime.now(pytz.timezone("Asia/Jakarta"))
        #st.session_state["bhvnMysql"].executeOperation(query=query)
        helper.add_userLogs(username, local_now, utc_now, activity)
        #date = local_now.date()
        #self.current_time = self.now.strftime("%H:%M:%S")

# def get_lat_lng():
#     g = geocoder.ip('me')
#     latlng= g.latlng
#     lat =latlng[0]
#     lng = latlng[1]
#     return lat , lng

# def get_local_time ():
#     t = time.localtime()
#     current_time = time.strftime("%H:%M:%S", t)
#     return current_time
#def get_timezone():
#    obj = TimezoneFinder()
#    lat, lng = get_lat_lng()
#    #ip = obj.ip_at(lng=lng, lat=lat)
#    time_zone = obj.timezone_at(lng=lng, lat=lat)
#    return time_zone

# def greetings():
#     now = get_local_time()[0:2]
#     if int(now) < 12 :
#         return 'Morning'
#     elif int(now) < 17 : 
#         return 'Afternoon'
#     else :
#         return 'Evening'


# conn = sqlite3.connect('users.db', check_same_thread=False)
# c = conn.cursor()

def get_user_rights(username):
    user_rights = helper.view_all_users()
    user_rights = pd.DataFrame(user_rights, columns=['User Name', 'Password', 'Assigned Rights'])
    user_rights = str(user_rights[user_rights['User Name'] == username]['Assigned Rights'].tolist())
    user_rights = user_rights[2:-2]
    user_rights = re.split(',', user_rights)
    #if 'Admin' in user_rights: user_rights.remove('Admin')
    return user_rights

def get_all_users():
    users = helper.view_all_users()
    users = pd.DataFrame(users, columns=['User Name', 'Password', 'Assigned Rights'])
    users = users['User Name'].tolist()
    return users

def user_entry(username, name, authenticator):

    # helper.create_usertable()
    # hashed_pswd = helper.make_hashes(password)
    # result = helper.login_user(username, helper.check_hashes(password, hashed_pswd))
    # if result:
    st.sidebar.success((f"Welcome, {str.title(name)}"))
    
    authenticator.logout("Logout", "sidebar")
    user_rights_ses = str(username)+"_user_rights"
    if user_rights_ses not in st.session_state:
        bhvnMysql = sqlDBManagement(host = helper.OLAP_HOST, username = helper.OLAP_USER_NAME,
                            password = helper.SQL_DWH_PASS, database = helper.OLAP_DB_NAME)
        user_rights = bhvnMysql.getDataFramebyQuery(f'SELECT rights FROM tblusers WHERE username="{username}"')
        user_rights = user_rights['rights'].tolist()[0]
        user_rights = [re.sub('[^A-Za-z0-9 &]+', '', right.strip()) for right in list(re.split(',', user_rights))]
        user_rights.insert(0, 'Make a Selection 👇')
        st.session_state[user_rights_ses] = user_rights
    else:
        user_rights = st.session_state[user_rights_ses]
    #user_rights = helper.get_all_rights()['Rights'].tolist()
    #user_rights.insert(0, 'Select the Department')
    # if username == 'gadmin' or username == 'Gadmin':
    #     user_rights.insert(-1, 'Delete User')
    #     user_rights.insert(-1, 'Rights Management')
    #task = st.sidebar.radio(
    #        'Deparment :', user_rights
    #        )
    with st.sidebar:
        task = option_menu(
            menu_title = "Departments",
            options = user_rights, 
            icons = ["arrow-down-square-fill"],
            menu_icon = ["building"]
        )
    return task
    # else:
    #     app_logger(username, 'Sign in')
    #     st.sidebar.error('Incorrect Username/Password! New here ? Please Contact Admin for your Account')

def create_new_user(username):
    #all_rights = ['HR & Compliance','Finance' ,'Purchase', 'Cutting','Printing', 'TPR', 'Automation', 'Sewing','Add New User','Users Dashboard','Update User', 'Update Password', 'Admin']
    
    all_rights_df = helper.get_all_rights()
    rights_list = all_rights_df['Rights'].tolist()
    st.header("Create New User Account")
    new_user = st.text_input("New Username")
    col1, col2 = st.columns(2)
    with col1:
        new_password = st.text_input("Assign Password", type = 'password')
    with col2:
        rights = st.multiselect("Assign Rights", rights_list)
    if 'Admin' in rights:
        rights = rights_list
    rights = ','.join([i for i in  rights])
    st.markdown(f"Rights Assigned : {rights}")
    if st.button('💼SignUp'):
        try:
            helper.create_usertable()
            helper.add_userdata(new_user.lower(), helper.make_hashes(new_password), rights)
            st.success(f'Dear {str.title(username)}, a new user with the name "{str.title(new_user)}" has been created in the system.')
            st.info("Please provide these login credentials along with the URL to the new user.")
            userManagement.app_logger(username, "New User Account")
            st.balloons()
        except:
            st.error(f'User with the name "{new_user}" already exists, kindly provide another username.')



def update_user(username):
    user_loggedin = username
    st.header('Update User')
    users = get_all_users()
    if user_loggedin != "gadmin" and user_loggedin != "Gadmin":
        users.remove('gadmin')
    username = st.selectbox('Select User : ' , users)
    current_rights = get_user_rights(username)
    all_rights = helper.get_all_rights()
    all_rights = all_rights['Rights'].tolist()
    if current_rights != ['']:
        user_rights = st.multiselect('User Rights : ', all_rights, default=current_rights)
    else: 
        user_rights = st.multiselect('User Rights : ', all_rights)
    if st.button('🏅Update User'):
        helper.update_rights_helper(username, user_rights)
        app_logger(user_loggedin, "User Updated")
        st.balloons()
def update_password(username):
    st.header('Update Password')
    st.write(fh.format_st_button(), unsafe_allow_html=True)
    col1 , col2 = st.columns(2)
    if username == 'gadmin':
        with col1:
            username_selection = st.session_state['all_users']
            username_selection = st.selectbox('User Name : ', username_selection)
    else: 
        with col1:
            username_selection = st.selectbox('User Name : ', [username])
    with col2:
        password = st.text_input('Enter the New Password : ', type='password')

    
    #updates
    if st.button('🔐Update Password'):
            
        if pwdValidator(pwd = password).validate_pwd():
            hashed = stauth.Hasher([password]).generate()[0]
            
            bhvnMysql = sqlDBManagement(host = helper.OLAP_HOST, username = helper.OLAP_USER_NAME,
            password = helper.SQL_DWH_PASS, database = helper.OLAP_DB_NAME)
            bhvnMysql.executeOperation(f'UPDATE tblusers SET pwd="{password}", password="{hashed}" WHERE username="{username_selection}"')
            st.success(f'Password for "{str.title(username_selection)}" has been updated')
            Security(username).pass_change_alert()
            app_logger(username, "Password Updated")
            st.balloons()
def del_user():
    st.header('Delete a User')
    st.write(fh.format_st_button(), unsafe_allow_html=True)
    users = get_all_users()
    users = [e for e in users if e not in ("admin", "gadmin")]
    user_to_del = st.selectbox('Select a User to delete :', users)
    st.error(f'User "{user_to_del}" will be permanently removed from the system, proceed with the caution')
    if st.button('❌Delete User'):
        helper.del_user_helper(username = user_to_del)
def render_admin(username):
    st.write('<style>div.row-widget.stButton > div{flex-direction:row;} </style>', unsafe_allow_html=True)
    st.write('<style>div.st-bf{flex-direction:column;} div.st-ag{font-weight:bold;padding-left:2px;}</style>', unsafe_allow_html=True)
    st.write(fh.format_st_button(), unsafe_allow_html=True)

    selection = option_menu(

                menu_title = "Admin",
                options = ['User Dashboard', 'Create New User', 'Update User Rights'],
                icons = ["bar-chart-fill", "person-plus-fill", "people"],
                menu_icon = ["person-workspace"],
                orientation = "horizontal"
    )

    try:
        if selection == 'User Dashboard':
            usersDashboard.render_usersDashboard(username)
        #elif st.session_state['new_user']:
        elif selection == 'Create New User':
            create_new_user(username)
        
        elif selection == 'Update User Rights':
            update_user(username)
    except:
        pass
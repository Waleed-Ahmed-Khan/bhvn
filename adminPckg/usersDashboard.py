from common import helper, vizHelper
import streamlit as st
import adminPckg.userManagement as userManagement
import static.formatHelper as fh
import pandas as pd
from st_aggrid import AgGrid
from static.formatHelper import hover_size


def add_rights():
    st.header("Add New Rights")
    st.write(fh.format_st_button(), unsafe_allow_html=True)
    rights = st.text_input('User Rights',value="", placeholder="Enter the new user right" )
    order = st.number_input("Enter the order : ", min_value=0, step=1)
    if st.button("✨ Add User Rights"):
        helper.create_allRights()
        helper.add_new_rights(rights, order)
        st.success(f'New right "{rights}" has been added successfully!')
def update_rights():
    st.header("Update Rights")
    st.write(fh.format_st_button(), unsafe_allow_html=True)
    all_rights_df = helper.get_all_rights()
    AgGrid(all_rights_df)
    rights_list = all_rights_df['Rights'].tolist()
    #rights_list.insert(0, "Select")
    rights = st.selectbox('User Right', rights_list)
    order = st.number_input("Enter the order : ", min_value=0, step=1)
    if st.button("🥋 Update Rights"):
        helper.update_rights_table(rights, order)
        st.success('Rights order uodated successfully!')
def delete_rights():
    st.header('Delet Rights')
    st.write(fh.format_st_button(), unsafe_allow_html=True)
    all_rights_df = helper.get_all_rights()
    st.dataframe(all_rights_df)
    rights_list = all_rights_df['Rights'].tolist()
    #rights_list.insert(0, "Select")
    rights = st.selectbox('User Right', rights_list)
    if st.button("❌ Delete Right"):
        helper.delete_rights_helper(rights)
        st.error(f'User Right "{rights}" has been deleted.')


def render_rightsManagement():
    st.write('<style>div.row-widget.stRadio > div{flex-direction:row;} </style>', unsafe_allow_html=True)
    st.write('<style>div.st-bf{flex-direction:column;} div.st-ag{font-weight:bold;padding-left:2px;}</style>', unsafe_allow_html=True)
    choose=st.radio("",("Add New Right","Update Rights","Delete Rights"))
    if choose == "Add New Right":
        add_rights()
    elif choose == "Update Rights":
        update_rights()
    elif choose == "Delete Rights":
        delete_rights()
    else:
        st.error('Somthing went wrong regarding your selection')

def render_usersDashboard(username):
    st.markdown(hover_size(), unsafe_allow_html=True)
    st.subheader('User Activity Logs')
    cursor_sql_olap , conn_sql_olap = helper.connect_sql_olap()
    user_logs = helper.get_user_logs(cursor_sql_olap, conn_sql_olap)
    
    user_result = helper.view_all_users()
    clean_df = pd.DataFrame(user_result, columns=['User Name', 'Password', 'Assigned Rights'])
    clean_df = clean_df.drop(clean_df[clean_df['User Name'] == 'gadmin'].index)
    active_users = clean_df['User Name']
    user_logs =  user_logs[user_logs['UserName'].isin(active_users)]
    user_logs['date_filter'] = user_logs['DateTimeUTC'].astype('datetime64').dt.strftime("%Y/%m/%d")
    date = user_logs['date_filter'].unique().tolist()
    all_users = user_logs['UserName'].unique().tolist()
    all_users.insert(0, 'All Users') 
    col1, col2, col3 =  st.columns(3)
    with col1:
        st.markdown("**Start Date :**")
        start_date = st.date_input('', pd.to_datetime(min(date)))
        #date_selection = st.slider('',min_value=min(date), max_value=max(date), value=(min(date),max(date))) 
    with col2:
        st.markdown("**End Date :**")
        end_date = st.date_input('', pd.to_datetime(max(date)))
        #end_date = pd.to_datetime("19/04/2022")
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
        AgGrid(clean_df)
        st.markdown('<hr/>', unsafe_allow_html = True)
        st.subheader('Download Activity Logs')
        #user_logs_disp = user_logs.drop(columns=['Month Number', 'Month', 'Day Number', 'Day', 'activity_count', 'date_filter']) 
        user_logs = user_logs.drop(columns=['Month Number', 'Month', 'Day Number', 'Day', 'activity_count', 'date_filter']) 
        AgGrid(user_logs)
        df_xlsx = helper.to_excel(user_logs)
        st.download_button(label='📥 Download User Logs',
                            data=df_xlsx ,
                            file_name= 'UserLogs.xlsx')
        userManagement.app_logger(username, "User Profiles")

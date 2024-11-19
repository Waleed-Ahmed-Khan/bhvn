import streamlit as st
import static.formatHelper as fh
from st_aggrid import AgGrid
from common import helper 
from common.sqlDBOperations import sqlDBManagement


bhvnMysql = sqlDBManagement(host = helper.OLAP_HOST, username = helper.OLAP_USER_NAME,
                            password = helper.SQL_DWH_PASS, database = helper.OLAP_DB_NAME)
def add_rights():
    st.header("Add New Rights")
    st.write(fh.format_st_button(), unsafe_allow_html=True)
    rights = st.text_input('User Rights',value="", placeholder="Enter the new user right" )
    if st.button("✨ Add User Rights"):
        try:
            query = f'INSERT INTO allrights(rights) VALUES ("{rights}");'
            bhvnMysql.executeOperation(query=query)
        except Exception as e:
            raise e
        st.success(f'New right "{rights}" has been added successfully!')
def delete_rights():
    st.header('Delet Rights')
    st.write(fh.format_st_button(), unsafe_allow_html=True)
    all_rights_df = bhvnMysql.getDataFramebyQuery(query = "SELECT * FROM allrights;")
    AgGrid(all_rights_df)
    rights_list = all_rights_df['rights'].tolist()
    #rights_list.insert(0, "Select")
    rights = st.selectbox('User Right', rights_list)
    if st.button("❌ Delete Right"):
        query = f'DELETE FROM allRights WHERE rights ="{rights}"'
        bhvnMysql.executeOperation(query=query)
        st.error(f'User Right "{rights}" has been deleted.')

def add_designation():
    st.header("Add New Designation")
    st.write(fh.format_st_button(), unsafe_allow_html=True)
    designation = st.text_input('Designation',value="", placeholder="Enter the new Designation name" )
    if st.button("✨ Add New Designation"):
        try:
            query = f'INSERT INTO tbldesignations(designation) VALUES ("{designation}");'
            bhvnMysql.executeOperation(query=query)
        except Exception as e:
            raise e
        st.success(f'New designation "{designation}" has been added successfully!')
def delete_designation():
    st.header('Delet designation')
    st.write(fh.format_st_button(), unsafe_allow_html=True)
    all_designations_df = bhvnMysql.getDataFramebyQuery(query = "SELECT * FROM tbldesignations;")
    AgGrid(all_designations_df)
    designations_list = all_designations_df['designation'].tolist()
    #rights_list.insert(0, "Select")
    designation = st.selectbox('Designations', designations_list)
    if st.button("❌ Delete Designation"):
        query = f'DELETE FROM tbldesignations WHERE designation ="{designation}"'
        bhvnMysql.executeOperation(query=query)
        st.error(f'Designation "{designation}" has been deleted.')

def add_customer():
    st.header("Add New Customer")
    st.write(fh.format_st_button(), unsafe_allow_html=True)
    customer = st.text_input('Customer',value="", placeholder="Enter the new Customer name" )
    if st.button("✨ Add New Customer"):
        try:
            query = f'INSERT INTO tblcustomers(customer) VALUES ("{customer}");'
            bhvnMysql.executeOperation(query=query)
        except Exception as e:
            raise e
        st.success(f'New customer "{customer}" has been added successfully!')
def delete_customer():
    st.header('Delet Customer')
    st.write(fh.format_st_button(), unsafe_allow_html=True)
    all_customers_df = bhvnMysql.getDataFramebyQuery(query = "SELECT * FROM tblcustomers;")
    AgGrid(all_customers_df)
    customers_list = all_customers_df['customer'].tolist()
    #rights_list.insert(0, "Select")
    customer = st.selectbox('Customers', customers_list)
    if st.button("❌ Delete Customer"):
        query = f'DELETE FROM tblcustomers WHERE customer ="{customer}"'
        bhvnMysql.executeOperation(query=query)
        st.error(f'Customer "{customer}" has been deleted.')
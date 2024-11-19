import streamlit as st
import helper
helper.create_usertable()
#helper.add_userdata('admin', helper.make_hashes('blue@321'), 'Admin')
#print('user created!')

#Assign Roles
def create_new_user(username):
    all_rights = ['Cutting','Printing','TPR', 'Automation', 'Sewing', 'Purchase', 'Update Password', 'Admin']
    st.header("Create New Account")
    new_user = st.text_input("New Username")
    new_password = st.text_input("Assign Password", type = 'password')
    rights = st.multiselect("Assign Rights", all_rights)
    if 'Admin' in rights:
        rights = all_rights
    rights = ','.join([i for i in  rights])
    st.markdown(rights)
    if st.button('SignUp'):
        helper.create_usertable()
        helper.add_userdata(new_user, helper.make_hashes(new_password), rights)
        st.success(f'Dear {username}, a new user with the name "{new_user}" has been created in the system.')
        st.info("Please provide these login credentials along with the URL to the new user.")
create_new_user("admin")
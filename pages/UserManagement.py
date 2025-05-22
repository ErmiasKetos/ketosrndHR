import streamlit as st
from utils.auth import get_all_users, add_user, delete_user
import pandas as pd

def show_user_management(username):
    st.title("User Management")
    
    # Check if user is admin
    if username != "admin":
        st.warning("Only admin users can access this page.")
        return
    
    # Get all users
    users = get_all_users()
    
    # Display users
    st.subheader("Existing Users")
    
    if users:
        users_df = pd.DataFrame(users)
        st.dataframe(users_df)
    else:
        st.info("No users found.")
    
    # Add new user
    st.subheader("Add New User")
    
    with st.form("add_user_form"):
        new_username = st.text_input("Username")
        new_name = st.text_input("Full Name")
        new_email = st.text_input("Email")
        new_password = st.text_input("Password", type="password")
        
        submitted = st.form_submit_button("Add User")
        
        if submitted:
            if new_username and new_name and new_email and new_password:
                # Check if username already exists
                if any(user['username'] == new_username for user in users):
                    st.error(f"Username '{new_username}' already exists.")
                else:
                    # Add user
                    success = add_user(new_username, new_name, new_email, new_password)
                    
                    if success:
                        st.success(f"User '{new_username}' added successfully.")
                        st.experimental_rerun()
                    else:
                        st.error("Failed to add user.")
            else:
                st.warning("Please fill in all fields.")
    
    # Delete user
    st.subheader("Delete User")
    
    if users:
        user_to_delete = st.selectbox(
            "Select a user to delete",
            [user['username'] for user in users if user['username'] != "admin"]
        )
        
        if user_to_delete:
            if st.button(f"Delete User '{user_to_delete}'"):
                # Delete user
                success = delete_user(user_to_delete)
                
                if success:
                    st.success(f"User '{user_to_delete}' deleted successfully.")
                    st.experimental_rerun()
                else:
                    st.error("Failed to delete user.")
    else:
        st.info("No users to delete.")

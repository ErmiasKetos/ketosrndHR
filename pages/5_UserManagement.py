import streamlit as st
from utils.db import get_db, User
from utils.auth import hash_password


def app():
    st.title("👥 User Management")
    st.write("Manage application users (add/remove).")

    db = get_db()
    users = User.select()
    # Display existing users
    user_rows = [{"ID": u.id, "Username": u.username, "Name": u.name} for u in users]
    st.table(user_rows)

    st.subheader("Add New User")
    new_username = st.text_input("Username (email)", key="add_username")
    new_name = st.text_input("Full Name", key="add_name")
    new_password = st.text_input("Password", type="password", key="add_password")
    if st.button("Add User", key="add_user_btn"):
        if new_username and new_password:
            hashed = hash_password(new_password)
            User.create(username=new_username, name=new_name, password=hashed)
            st.success(f"User '{new_username}' added.")
            st.experimental_rerun()
        else:
            st.error("Please provide both username and password.")

    st.subheader("Delete User")
    delete_username = st.selectbox(
        "Select user to delete", 
        options=[u.username for u in users],
        key="delete_username"
    )
    if st.button("Delete User", key="del_user_btn"):
        if delete_username:
            user_to_del = User.get(User.username == delete_username)
            user_to_del.delete_instance()
            st.success(f"User '{delete_username}' deleted.")
            st.experimental_rerun()
        else:
            st.error("No user selected.")


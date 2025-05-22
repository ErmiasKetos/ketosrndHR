import streamlit as st
import yaml
import os
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from pathlib import Path

# Function to check authentication
def check_authentication():
    # Initialize session state for authentication
    if 'authentication_status' not in st.session_state:
        st.session_state['authentication_status'] = None
    if 'username' not in st.session_state:
        st.session_state['username'] = None
    if 'name' not in st.session_state:
        st.session_state['name'] = None
    
    # Load configuration from YAML file
    config_file = Path("config.yaml")
    
    # Create default config if it doesn't exist
    if not config_file.exists():
        default_config = {
            'credentials': {
                'usernames': {
                    'admin': {
                        'email': 'admin@example.com',
                        'name': 'Admin User',
                        'password': stauth.Hasher(['password']).generate()[0]
                    }
                }
            },
            'cookie': {
                'expiry_days': 30,
                'key': 'resume_screening_auth',
                'name': 'resume_screening_cookie'
            }
        }
        with open(config_file, 'w') as file:
            yaml.dump(default_config, file, default_flow_style=False)
    
    # Load configuration
    with open(config_file) as file:
        config = yaml.load(file, Loader=SafeLoader)
    
    # Create authenticator
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )
    
    # Display login form if not authenticated
    if st.session_state['authentication_status'] is not True:
        st.title("KETOS Resume Screening")
        name, authentication_status, username = authenticator.login("Login", "main")
        
        st.session_state['authentication_status'] = authentication_status
        st.session_state['username'] = username
        st.session_state['name'] = name
        
        if authentication_status is False:
            st.error("Username/password is incorrect")
            return False, None
        elif authentication_status is None:
            st.warning("Please enter your username and password")
            return False, None
    
    return True, st.session_state['username']

# Function to add a new user
def add_user(username, name, email, password):
    config_file = Path("config.yaml")
    
    with open(config_file) as file:
        config = yaml.load(file, Loader=SafeLoader)
    
    # Hash the password
    hashed_password = stauth.Hasher([password]).generate()[0]
    
    # Add the new user
    config['credentials']['usernames'][username] = {
        'email': email,
        'name': name,
        'password': hashed_password
    }
    
    # Save the updated configuration
    with open(config_file, 'w') as file:
        yaml.dump(config, file, default_flow_style=False)
    
    return True

# Function to delete a user
def delete_user(username):
    config_file = Path("config.yaml")
    
    with open(config_file) as file:
        config = yaml.load(file, Loader=SafeLoader)
    
    # Check if the user exists
    if username in config['credentials']['usernames']:
        # Delete the user
        del config['credentials']['usernames'][username]
        
        # Save the updated configuration
        with open(config_file, 'w') as file:
            yaml.dump(config, file, default_flow_style=False)
        
        return True
    
    return False

# Function to get all users
def get_all_users():
    config_file = Path("config.yaml")
    
    with open(config_file) as file:
        config = yaml.load(file, Loader=SafeLoader)
    
    users = []
    for username, user_data in config['credentials']['usernames'].items():
        users.append({
            'username': username,
            'name': user_data['name'],
            'email': user_data['email']
        })
    
    return users

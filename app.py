import streamlit as st
from streamlit_option_menu import option_menu
import os
import sys

# Add the current directory to the path so we can import from utils
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import utilities
from utils.auth import check_authentication
from utils.db import initialize_database

# Set page configuration
st.set_page_config(
    page_title="KETOS Resume Screening",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
initialize_database()

# Check authentication
authenticated, username = check_authentication()

if not authenticated:
    st.stop()

# Main navigation
with st.sidebar:
    st.image("assets/ketos_logo.png", width=200)
    
    selected = option_menu(
        menu_title="Navigation",
        options=["Job Setup", "Resume Upload", "Screening Dashboard", "User Management"],
        icons=["briefcase", "upload", "table", "people"],
        menu_icon="cast",
        default_index=0,
    )

# Route to the appropriate page based on selection
if selected == "Job Setup":
    from pages.job_setup import show_job_setup
    show_job_setup(username)
elif selected == "Resume Upload":
    from pages.upload_and_criteria import show_upload_and_criteria
    show_upload_and_criteria(username)
elif selected == "Screening Dashboard":
    from pages.dashboard import show_dashboard
    show_dashboard(username)
elif selected == "User Management":
    from pages.user_management import show_user_management
    show_user_management(username)

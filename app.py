import streamlit as st
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
    
    # Simple navigation with radio buttons
    pages = ["Job Setup", "Resume Upload", "Screening Dashboard", "NLP Insights", "User Management"]
    icons = ["📋", "📤", "📊", "🧠", "👥"]
    
    st.markdown("## Navigation")
    
    for i, (page, icon) in enumerate(zip(pages, icons)):
        if st.sidebar.button(f"{icon} {page}", key=f"nav_{i}", use_container_width=True):
            st.session_state.page = page
    
    # Initialize page state if not set
    if "page" not in st.session_state:
        st.session_state.page = "Job Setup"

# Route to the appropriate page based on selection
if st.session_state.page == "Job Setup":
    from pages.job_setup import show_job_setup
    show_job_setup(username)
elif st.session_state.page == "Resume Upload":
    from pages.upload_and_criteria import show_upload_and_criteria
    show_upload_and_criteria(username)
elif st.session_state.page == "Screening Dashboard":
    from pages.dashboard import show_dashboard
    show_dashboard(username)
elif st.session_state.page == "NLP Insights":
    from pages.nlp_insights import show_nlp_insights
    show_nlp_insights(username)
elif st.session_state.page == "User Management":
    from pages.user_management import show_user_management
    show_user_management(username)

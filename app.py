import streamlit as st

# Set page configuration before any other Streamlit commands
st.set_page_config(
    page_title="KETOS Resume Screening",
    layout="wide"
)

# Import page modules
from pages.Login import app as login_page
from pages.JobSetup import app as job_setup_page
from pages.UploadAndCriteria import app as upload_page
from pages.Dashboard import app as dashboard_page
from pages.UserManagement import app as user_mgmt_page

# Registry of pages for navigation
PAGES = {
    "Login": login_page,
    "Job Setup": job_setup_page,
    "Upload & Criteria": upload_page,
    "Screening Dashboard": dashboard_page,
    "User Management": user_mgmt_page
}

def main():
    # Initialize authentication flag
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    # If not authenticated, show Login page
    if not st.session_state.authenticated:
        PAGES["Login"]()
        return

    # Authenticated: show navigation
    st.sidebar.title("Navigation")
    choice = st.sidebar.selectbox(
        "Go to", list(PAGES.keys())[1:]  # skip Login
    )
    page = PAGES[choice]
    page()

if __name__ == "__main__":
    main()

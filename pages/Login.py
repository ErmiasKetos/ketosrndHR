import streamlit as st
import streamlit_authenticator as stauth
import yaml

# Load authentication config from Streamlit secrets
@st.cache(allow_output_mutation=True)
def load_auth_config():
    # Secrets.toml should include a `credentials` section with hashed passwords
    return st.secrets["credentials"]


def app():
    st.title("🔒 KETOS Resume Screening - Login")

    config = load_auth_config()
    authenticator = stauth.Authenticate(
        config['usernames'],
        cookie_name="ketos_auth",
        key="some_random_signature_key",
        cookie_expiry_days=30,
    )

    name, auth_status, username = authenticator.login("Login", "main")

    if auth_status:
        st.session_state.authenticated = True
        st.session_state.username = username
        # Render a logout button in the sidebar
        authenticator.logout("Logout", "sidebar")
        st.experimental_rerun()

    elif auth_status is False:
        st.error("Username/password is incorrect")
    else:
        st.info("Please enter your username and password to continue.")

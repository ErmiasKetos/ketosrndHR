import streamlit as st
from utils.parser import parse_job_description, parse_criteria
from utils.db import get_db, Job


def app():
    st.title("📄 Job Setup")
    st.write("Define the job you are hiring for and the screening criteria.")

    # Input Job Title
    job_title = st.text_input("Job Title")

    # JD input: free-text or file upload
    jd_option = st.radio("Job Description Input", ["Paste Text", "Upload PDF/Word File"])
    if jd_option == "Paste Text":
        jd_text = st.text_area("Paste the Job Description here")
    else:
        jd_file = st.file_uploader("Upload Job Description File", type=["pdf", "docx"])
        if jd_file:
            jd_text = parse_job_description(jd_file)
        else:
            jd_text = ""

    # Criteria input: paste bullets or upload file
    crit_option = st.radio("Screening Criteria Input", ["Paste Bullet List", "Upload Criteria File"])
    if crit_option == "Paste Bullet List":
        crit_text = st.text_area("Paste each criterion on a new line")
    else:
        crit_file = st.file_uploader("Upload Criteria File", type=["pdf", "docx"] , key="file_crit")
        if crit_file:
            crit_text = parse_criteria(crit_file)
        else:
            crit_text = ""

    # Preview and approve criteria
    if jd_text and crit_text:
        st.subheader("Preview Criteria")
        criteria_list = crit_text.splitlines()
        approved = st.multiselect("Select criteria to include", criteria_list, default=criteria_list)

        if st.button("Save Job Setup"):
            # Save job and approved criteria to DB
            db = get_db()
            job = Job.create(title=job_title, description=jd_text, criteria=approved)
            st.success(f"Job '{job_title}' saved with {len(approved)} criteria.")
    else:
        st.info("Please provide both a Job Description and Screening Criteria.")

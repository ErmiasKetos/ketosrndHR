import streamlit as st
from utils.db import save_job, save_criteria, get_jobs, get_job, get_criteria
import pandas as pd
import re

def extract_criteria_from_text(text):
    """Extract criteria from job description text."""
    lines = text.split('\n')
    criteria = []
    
    for line in lines:
        line = line.strip()
        if line.startswith('•') or line.startswith('-') or line.startswith('*'):
            criterion = line[1:].strip()
            if criterion:
                criteria.append({
                    'text': criterion,
                    'weight': 1,
                    'required': False
                })
    
    return criteria

def show_job_setup(username):
    st.title("Job Setup")
    
    # Get existing jobs
    jobs = get_jobs(username)
    
    # Create tabs for new job and existing jobs
    tab1, tab2 = st.tabs(["Create New Job", "View Existing Jobs"])
    
    with tab1:
        st.header("Create a New Job")
        
        # Job title
        job_title = st.text_input("Job Title")
        
        # Job description
        job_description = st.text_area("Job Description", height=200)
        
        # Extract criteria button
        if st.button("Extract Criteria from Description"):
            if job_description:
                criteria = extract_criteria_from_text(job_description)
                
                if criteria:
                    st.session_state['extracted_criteria'] = criteria
                    st.success(f"Extracted {len(criteria)} criteria from the job description.")
                else:
                    st.warning("No criteria could be extracted. Please format your requirements as bullet points (•, -, or *).")
            else:
                st.warning("Please enter a job description first.")
        
        # Display and edit extracted criteria
        if 'extracted_criteria' in st.session_state:
            st.subheader("Criteria")
            
            criteria_df = pd.DataFrame(st.session_state['extracted_criteria'])
            
            # Create columns for each criterion
            for i, criterion in enumerate(st.session_state['extracted_criteria']):
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.session_state['extracted_criteria'][i]['text'] = st.text_input(
                        f"Criterion {i+1}",
                        value=criterion['text'],
                        key=f"criterion_{i}"
                    )
                
                with col2:
                    st.session_state['extracted_criteria'][i]['weight'] = st.number_input(
                        "Weight",
                        min_value=1,
                        max_value=10,
                        value=criterion['weight'],
                        key=f"weight_{i}"
                    )
                
                with col3:
                    st.session_state['extracted_criteria'][i]['required'] = st.checkbox(
                        "Required",
                        value=criterion['required'],
                        key=f"required_{i}"
                    )
            
            # Add new criterion button
            if st.button("Add Criterion"):
                st.session_state['extracted_criteria'].append({
                    'text': "",
                    'weight': 1,
                    'required': False
                })
                st.experimental_rerun()
        
        # Save job button
        if st.button("Save Job"):
            if job_title and job_description and 'extracted_criteria' in st.session_state:
                # Save job
                job_id = save_job(job_title, job_description, username)
                
                # Save criteria
                save_criteria(job_id, st.session_state['extracted_criteria'])
                
                st.success(f"Job '{job_title}' saved successfully!")
                
                # Clear session state
                del st.session_state['extracted_criteria']
                
                # Refresh jobs
                jobs = get_jobs(username)
            else:
                st.warning("Please fill in all fields and extract criteria before saving.")
    
    with tab2:
        st.header("Existing Jobs")
        
        if jobs.empty:
            st.info("No jobs found. Create a new job to get started.")
        else:
            # Display jobs in a table
            st.dataframe(
                jobs[['id', 'title', 'created_at']],
                column_config={
                    "id": "Job ID",
                    "title": "Job Title",
                    "created_at": "Created At"
                },
                hide_index=True
            )
            
            # Select job to view details
            job_id = st.selectbox("Select a job to view details", jobs['id'].tolist(), format_func=lambda x: jobs[jobs['id'] == x]['title'].iloc[0])
            
            if job_id:
                # Get job details
                job = get_job(job_id)
                criteria = get_criteria(job_id)
                
                # Display job details
                st.subheader(f"Job: {job['title']}")
                st.write(f"Created by: {job['created_by']}")
                st.write(f"Created at: {job['created_at']}")
                
                # Display job description
                st.markdown("### Job Description")
                st.write(job['description'])
                
                # Display criteria
                st.markdown("### Criteria")
                
                if criteria.empty:
                    st.info("No criteria found for this job.")
                else:
                    for _, criterion in criteria.iterrows():
                        required_text = " (Required)" if criterion['required'] else ""
                        st.write(f"• {criterion['criterion']} - Weight: {criterion['weight']}{required_text}")

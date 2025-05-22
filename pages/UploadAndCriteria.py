import streamlit as st
import pandas as pd
import os
from utils.db import get_jobs, get_job, get_criteria, save_candidate
from utils.parser import parse_resume, save_uploaded_file
from utils.screening import screen_candidate

def show_upload_and_criteria(username):
    st.title("Resume Upload & Screening")
    
    # Get jobs created by the user
    jobs = get_jobs(username)
    
    if jobs.empty:
        st.warning("No jobs found. Please create a job first.")
        return
    
    # Select job
    job_id = st.selectbox(
        "Select a job",
        jobs['id'].tolist(),
        format_func=lambda x: jobs[jobs['id'] == x]['title'].iloc[0]
    )
    
    if job_id:
        # Get job details and criteria
        job = get_job(job_id)
        criteria = get_criteria(job_id)
        
        if criteria.empty:
            st.warning("No criteria found for this job. Please add criteria first.")
            return
        
        st.subheader(f"Upload Resumes for: {job['title']}")
        
        # Display criteria
        with st.expander("View Job Criteria"):
            for _, criterion in criteria.iterrows():
                required_text = " (Required)" if criterion['required'] else ""
                st.write(f"• {criterion['criterion']} - Weight: {criterion['weight']}{required_text}")
        
        # Upload resumes
        uploaded_files = st.file_uploader(
            "Upload Resumes (PDF or DOCX)",
            type=["pdf", "docx"],
            accept_multiple_files=True
        )
        
        if uploaded_files:
            if st.button(f"Process {len(uploaded_files)} Resume(s)"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                results = []
                
                for i, uploaded_file in enumerate(uploaded_files):
                    status_text.text(f"Processing {uploaded_file.name}...")
                    
                    # Save the uploaded file
                    file_path = save_uploaded_file(uploaded_file)
                    
                    # Parse the resume
                    parsed_data = parse_resume(file_path)
                    
                    if parsed_data:
                        # Screen the candidate
                        screening_result = screen_candidate(parsed_data, criteria, job['description'])
                        
                        # Prepare candidate data
                        candidate_data = {
                            'name': parsed_data['name'],
                            'email': parsed_data['email'],
                            'phone': parsed_data['phone'],
                            'education': parsed_data['education'],
                            'experience': parsed_data['experience'],
                            'skills': parsed_data['skills'],
                            'resume_path': file_path,
                            'score': screening_result['score'],
                            'passed': screening_result['passed'],
                            'summary': screening_result['summary'],
                            'nlp_results': screening_result.get('nlp_results', {})
                        }
                        
                        # Save candidate to database
                        candidate_id = save_candidate(job_id, candidate_data)
                        
                        # Add to results
                        results.append({
                            'File': uploaded_file.name,
                            'Name': parsed_data['name'],
                            'Email': parsed_data['email'],
                            'Score': f"{screening_result['score']:.1f}%",
                            'Status': "Pass" if screening_result['passed'] else "Fail",
                            'Summary': screening_result['summary']
                        })
                    
                    # Update progress
                    progress_bar.progress((i + 1) / len(uploaded_files))
                
                # Display results
                status_text.text("Processing complete!")
                
                if results:
                    st.subheader("Processing Results")
                    results_df = pd.DataFrame(results)
                    st.dataframe(results_df)
                    
                    # Count passes and fails
                    passes = sum(1 for result in results if result['Status'] == "Pass")
                    fails = len(results) - passes
                    
                    st.success(f"Processed {len(results)} resumes: {passes} passed, {fails} failed.")
                    st.info("View the Screening Dashboard to see all candidates and take further actions.")
                else:
                    st.error("No resumes could be processed. Please check the file formats and try again.")

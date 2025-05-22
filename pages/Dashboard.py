import streamlit as st
import pandas as pd
from utils.db import get_jobs, get_candidates, update_candidate_status
import base64

def get_download_link(file_path, link_text):
    """Generate a download link for a file."""
    with open(file_path, "rb") as file:
        contents = file.read()
    
    b64 = base64.b64encode(contents).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{file_path.split("/")[-1]}">{link_text}</a>'
    return href

def show_candidate_details(candidate):
    """Show detailed information about a candidate."""
    st.subheader(f"Candidate: {candidate['name']}")
    
    # Basic information
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"**Email:** {candidate['email']}")
    with col2:
        st.write(f"**Phone:** {candidate['phone']}")
    with col3:
        st.write(f"**Score:** {candidate['score']:.1f}%")
    
    # Resume summary
    st.markdown("### Resume Summary")
    st.write(candidate['summary'])
    
    # Education
    if candidate['education']:
        st.markdown("### Education")
        st.write(candidate['education'])
    
    # Experience
    if candidate['experience']:
        st.markdown("### Experience")
        st.write(candidate['experience'])
    
    # Skills
    if candidate['skills']:
        st.markdown("### Skills")
        st.write(candidate['skills'])
    
    # Resume download
    if candidate['resume_path']:
        st.markdown(f"### Resume")
        st.markdown(get_download_link(candidate['resume_path'], "Download Resume"), unsafe_allow_html=True)

def show_dashboard(username):
    st.title("Screening Dashboard")
    
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
        # Get candidates for the job
        show_passed_only = st.checkbox("Show Passed Candidates Only", value=True)
        candidates = get_candidates(job_id, passed_only=show_passed_only)
        
        if candidates.empty:
            st.info("No candidates found for this job.")
            return
        
        # Prepare data for display
        display_data = candidates[['id', 'name', 'email', 'phone', 'score', 'passed', 'advanced', 'summary']].copy()
        display_data['score'] = display_data['score'].apply(lambda x: f"{x:.1f}%")
        display_data['passed'] = display_data['passed'].apply(lambda x: "Pass" if x else "Fail")
        display_data['advanced'] = display_data['advanced'].apply(lambda x: "Yes" if x else "No")
        
        # Add resume link column
        display_data['resume'] = candidates['resume_path'].apply(
            lambda x: "Download" if x else ""
        )
        
        # Display the dataframe
        st.subheader("Candidates")
        st.dataframe(display_data)
        
        # Advanced status management
        st.subheader("Update Advanced Status")
        
        # Create a selection mechanism
        selected_candidate = st.selectbox(
            "Select a candidate to update status",
            display_data['name'].tolist()
        )
        
        if selected_candidate:
            # Get the selected candidate's current status
            selected_idx = display_data[display_data['name'] == selected_candidate].index[0]
            selected_id = display_data.loc[selected_idx, 'id']
            current_status = display_data.loc[selected_idx, 'advanced'] == "Yes"
            
            # Create a toggle for the status
            new_status = st.checkbox(
                "Advanced to Next Stage",
                value=current_status,
                key=f"advanced_{selected_id}"
            )
            
            # Update button
            if st.button("Update Status"):
                update_candidate_status(selected_id, new_status)
                st.success(f"Updated status for {selected_candidate}")
                st.experimental_rerun()
        
        # View candidate details
        st.subheader("Candidate Details")
        candidate_to_view = st.selectbox(
            "Select a candidate to view details",
            display_data['name'].tolist(),
            key="view_candidate"
        )
        
        if candidate_to_view:
            # Get the selected candidate
            view_idx = display_data[display_data['name'] == candidate_to_view].index[0]
            view_id = display_data.loc[view_idx, 'id']
            selected_candidate = candidates[candidates['id'] == view_id].iloc[0]
            
            # Show candidate details
            show_candidate_details(selected_candidate)
        
        # Summary statistics
        st.subheader("Summary Statistics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_candidates = len(candidates)
            st.metric("Total Candidates", total_candidates)
        
        with col2:
            passed_candidates = candidates['passed'].sum()
            pass_rate = passed_candidates / total_candidates * 100 if total_candidates > 0 else 0
            st.metric("Passed Candidates", f"{passed_candidates} ({pass_rate:.1f}%)")
        
        with col3:
            advanced_candidates = candidates['advanced'].sum()
            advanced_rate = advanced_candidates / passed_candidates * 100 if passed_candidates > 0 else 0
            st.metric("Advanced to Next Stage", f"{advanced_candidates} ({advanced_rate:.1f}%)")
        
        # Export options
        st.subheader("Export Options")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Export All Candidates to CSV"):
                csv = candidates.to_csv(index=False)
                b64 = base64.b64encode(csv.encode()).decode()
                href = f'<a href="data:file/csv;base64,{b64}" download="candidates.csv">Download CSV</a>'
                st.markdown(href, unsafe_allow_html=True)
        
        with col2:
            if st.button("Export Advanced Candidates to CSV"):
                advanced = candidates[candidates['advanced'] == True]
                if not advanced.empty:
                    csv = advanced.to_csv(index=False)
                    b64 = base64.b64encode(csv.encode()).decode()
                    href = f'<a href="data:file/csv;base64,{b64}" download="advanced_candidates.csv">Download CSV</a>'
                    st.markdown(href, unsafe_allow_html=True)
                else:
                    st.warning("No advanced candidates to export.")

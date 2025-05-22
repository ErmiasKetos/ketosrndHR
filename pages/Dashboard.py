import streamlit as st
import pandas as pd
from utils.db import get_jobs, get_candidates, update_candidate_status
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
import base64

def get_download_link(file_path, link_text):
    """Generate a download link for a file."""
    with open(file_path, "rb") as file:
        contents = file.read()
    
    b64 = base64.b64encode(contents).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{file_path.split("/")[-1]}">{link_text}</a>'
    return href

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
        
        # Add resume link
        display_data['resume'] = candidates['resume_path'].apply(
            lambda x: get_download_link(x, "Download")
        )
        
        # Configure grid options
        gb = GridOptionsBuilder.from_dataframe(display_data)
        gb.configure_column("id", headerName="ID", hide=True)
        gb.configure_column("name", headerName="Name", width=150)
        gb.configure_column("email", headerName="Email", width=200)
        gb.configure_column("phone", headerName="Phone", width=150)
        gb.configure_column("score", headerName="Score", width=100)
        gb.configure_column("passed", headerName="Status", width=100)
        gb.configure_column("advanced", headerName="Advanced", width=100, editable=True)
        gb.configure_column("summary", headerName="Summary", width=300)
        gb.configure_column("resume", headerName="Resume", width=100)
        
        # Add checkbox selection
        gb.configure_selection(selection_mode="multiple", use_checkbox=True)
        
        # Configure grid options
        grid_options = gb.build()
        
        # Display the grid
        st.subheader("Candidates")
        grid_response = AgGrid(
            display_data,
            gridOptions=grid_options,
            update_mode="MODEL_CHANGED",
            fit_columns_on_grid_load=False,
            allow_unsafe_jscode=True,
            enable_enterprise_modules=False,
            height=400,
            width="100%"
        )
        
        # Get selected rows
        selected_rows = grid_response["selected_rows"]
        
        # Actions for selected candidates
        if selected_rows:
            st.subheader("Actions")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button(f"Advance {len(selected_rows)} Selected Candidate(s)"):
                    for row in selected_rows:
                        update_candidate_status(row["id"], True)
                    st.success(f"Advanced {len(selected_rows)} candidate(s) to the next stage.")
                    st.experimental_rerun()
            
            with col2:
                if st.button(f"Remove {len(selected_rows)} Selected Candidate(s) from Advanced"):
                    for row in selected_rows:
                        update_candidate_status(row["id"], False)
                    st.success(f"Removed {len(selected_rows)} candidate(s) from advanced stage.")
                    st.experimental_rerun()
        
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

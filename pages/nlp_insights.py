import streamlit as st
import pandas as pd
import json
from utils.db import get_jobs, get_candidates, get_criteria
from utils.visualization import (
    plot_similarity_heatmap,
    plot_candidate_embeddings,
    plot_skill_distribution,
    plot_experience_distribution
)

def show_nlp_insights(username):
    st.title("NLP Insights")
    
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
        candidates = get_candidates(job_id)
        criteria = get_criteria(job_id)
        
        if candidates.empty:
            st.info("No candidates found for this job.")
            return
        
        # Check if we have NLP results
        has_nlp_results = False
        for _, candidate in candidates.iterrows():
            if candidate['nlp_results']:
                has_nlp_results = True
                break
        
        if not has_nlp_results:
            st.warning("No NLP analysis results found. Please process resumes with the NLP-enhanced screening.")
            return
        
        # Create tabs for different visualizations
        tab1, tab2, tab3, tab4 = st.tabs([
            "Similarity Heatmap", 
            "Candidate Map", 
            "Skill Distribution",
            "Experience Distribution"
        ])
        
        with tab1:
            st.header("Candidate-Criteria Similarity")
            st.write("This heatmap shows how well each candidate matches each criterion based on semantic similarity.")
            plot_similarity_heatmap(candidates, criteria)
        
        with tab2:
            st.header("Candidate Similarity Map")
            st.write("This visualization shows candidates positioned in 2D space based on their similarity to each other.")
            plot_candidate_embeddings(candidates)
        
        with tab3:
            st.header("Skill Distribution")
            st.write("This chart shows the most common skills found across all candidates.")
            plot_skill_distribution(candidates)
        
        with tab4:
            st.header("Experience Distribution")
            st.write("This chart shows the years of experience for each candidate.")
            plot_experience_distribution(candidates)
        
        # Detailed NLP insights for individual candidates
        st.header("Individual Candidate Insights")
        
        # Select a candidate
        candidate_names = candidates['name'].tolist()
        selected_candidate_name = st.selectbox("Select a candidate", candidate_names)
        
        if selected_candidate_name:
            # Get the selected candidate
            selected_candidate = candidates[candidates['name'] == selected_candidate_name].iloc[0]
            
            # Display NLP insights
            if selected_candidate['nlp_results']:
                try:
                    nlp_results = json.loads(selected_candidate['nlp_results'])
                    
                    # Overall similarity
                    st.metric(
                        "Overall Match Score", 
                        f"{nlp_results.get('overall_similarity', 0) * 100:.1f}%"
                    )
                    
                    # Create columns for different insights
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Skills matched
                        st.subheader("Skills Matched")
                        skills = nlp_results.get('skills_matched', [])
                        if skills:
                            for skill in skills:
                                st.write(f"• {skill}")
                        else:
                            st.write("No skills matched.")
                        
                        # Job titles
                        st.subheader("Detected Job Titles")
                        titles = nlp_results.get('job_titles', [])
                        if titles:
                            for title in titles:
                                st.write(f"• {title}")
                        else:
                            st.write("No job titles detected.")
                    
                    with col2:
                        # Education
                        st.subheader("Education")
                        education = nlp_results.get('education', [])
                        if education:
                            for edu in education:
                                st.write(f"• {edu}")
                        else:
                            st.write("No education information detected.")
                        
                        # Experience
                        st.subheader("Experience")
                        st.write(f"Years of experience: {nlp_results.get('experience_years', 'Not detected')}")
                    
                    # Criteria matches
                    st.subheader("Criteria Matches")
                    criteria_matches = nlp_results.get('criteria_matches', [])
                    
                    if criteria_matches:
                        # Create a DataFrame for the criteria matches
                        matches_df = pd.DataFrame(criteria_matches)
                        matches_df['similarity'] = matches_df['similarity'].apply(lambda x: f"{x*100:.1f}%")
                        
                        # Display as a table
                        st.dataframe(
                            matches_df,
                            column_config={
                                "criterion": "Criterion",
                                "similarity": "Match Score"
                            },
                            hide_index=True
                        )
                    else:
                        st.write("No criteria matches found.")
                
                except Exception as e:
                    st.error(f"Error parsing NLP results: {e}")
            else:
                st.warning("No NLP analysis results found for this candidate.")

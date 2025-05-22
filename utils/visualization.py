import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
from sklearn.manifold import TSNE
import plotly.express as px
import plotly.graph_objects as go

def plot_similarity_heatmap(candidates, criteria):
    """Plot a heatmap of candidate-criteria similarity."""
    # Extract data
    candidate_names = []
    criterion_names = []
    similarity_data = []
    
    for _, candidate in candidates.iterrows():
        if candidate['nlp_results']:
            try:
                nlp_results = json.loads(candidate['nlp_results'])
                criteria_matches = nlp_results.get('criteria_matches', [])
                
                candidate_names.append(candidate['name'])
                
                # Extract similarities for each criterion
                row_data = []
                for _, criterion in criteria.iterrows():
                    criterion_text = criterion['criterion']
                    if criterion_text not in criterion_names:
                        criterion_names.append(criterion_text)
                    
                    # Find the similarity for this criterion
                    match = next((item for item in criteria_matches 
                                if item['criterion'].lower() == criterion_text.lower()), None)
                    
                    similarity = match['similarity'] if match else 0
                    row_data.append(similarity)
                
                similarity_data.append(row_data)
            except:
                pass
    
    if not similarity_data:
        st.warning("No similarity data available for visualization.")
        return
    
    # Create a DataFrame for the heatmap
    df = pd.DataFrame(similarity_data, index=candidate_names, columns=criterion_names)
    
    # Create a heatmap using Plotly
    fig = px.imshow(
        df,
        labels=dict(x="Criteria", y="Candidates", color="Similarity"),
        x=criterion_names,
        y=candidate_names,
        color_continuous_scale="Viridis",
        aspect="auto"
    )
    
    fig.update_layout(
        title="Candidate-Criteria Similarity Heatmap",
        xaxis_title="Criteria",
        yaxis_title="Candidates",
        height=500,
        width=800
    )
    
    st.plotly_chart(fig)

def plot_candidate_embeddings(candidates):
    """Plot candidate embeddings in 2D space using t-SNE."""
    # Extract embeddings
    names = []
    scores = []
    passed = []
    embeddings = []
    
    for _, candidate in candidates.iterrows():
        if candidate['nlp_results']:
            try:
                nlp_results = json.loads(candidate['nlp_results'])
                
                # We don't actually store the embeddings in the database
                # This is a placeholder for demonstration
                # In a real implementation, you would store and retrieve the embeddings
                
                # For now, we'll use the criteria similarities as a proxy
                criteria_matches = nlp_results.get('criteria_matches', [])
                if criteria_matches:
                    # Use similarities as a feature vector
                    embedding = [match['similarity'] for match in criteria_matches]
                    
                    # Only use if we have enough dimensions
                    if len(embedding) >= 3:
                        names.append(candidate['name'])
                        scores.append(candidate['score'])
                        passed.append("Pass" if candidate['passed'] else "Fail")
                        embeddings.append(embedding)
            except:
                pass
    
    if not embeddings:
        st.warning("No embedding data available for visualization.")
        return
    
    # Pad embeddings to the same length
    max_length = max(len(emb) for emb in embeddings)
    padded_embeddings = [emb + [0] * (max_length - len(emb)) for emb in embeddings]
    
    # Convert to numpy array
    embeddings_array = np.array(padded_embeddings)
    
    # Apply t-SNE for dimensionality reduction
    tsne = TSNE(n_components=2, random_state=42)
    embeddings_2d = tsne.fit_transform(embeddings_array)
    
    # Create a DataFrame for plotting
    df = pd.DataFrame({
        'x': embeddings_2d[:, 0],
        'y': embeddings_2d[:, 1],
        'name': names,
        'score': scores,
        'status': passed
    })
    
    # Create a scatter plot using Plotly
    fig = px.scatter(
        df,
        x='x',
        y='y',
        color='status',
        size='score',
        hover_name='name',
        text='name',
        title="Candidate Similarity Map",
        color_discrete_map={"Pass": "green", "Fail": "red"}
    )
    
    fig.update_traces(textposition='top center')
    
    fig.update_layout(
        height=600,
        width=800,
        xaxis_title="t-SNE Dimension 1",
        yaxis_title="t-SNE Dimension 2"
    )
    
    st.plotly_chart(fig)

def plot_skill_distribution(candidates):
    """Plot the distribution of skills across candidates."""
    # Extract skills
    all_skills = {}
    
    for _, candidate in candidates.iterrows():
        if candidate['nlp_results']:
            try:
                nlp_results = json.loads(candidate['nlp_results'])
                skills = nlp_results.get('skills_matched', [])
                
                for skill in skills:
                    if skill in all_skills:
                        all_skills[skill] += 1
                    else:
                        all_skills[skill] = 1
            except:
                pass
    
    if not all_skills:
        st.warning("No skill data available for visualization.")
        return
    
    # Sort skills by frequency
    sorted_skills = dict(sorted(all_skills.items(), key=lambda x: x[1], reverse=True))
    
    # Take top 15 skills
    top_skills = dict(list(sorted_skills.items())[:15])
    
    # Create a bar chart using Plotly
    fig = px.bar(
        x=list(top_skills.keys()),
        y=list(top_skills.values()),
        labels={'x': 'Skill', 'y': 'Count'},
        title="Top Skills Among Candidates"
    )
    
    fig.update_layout(
        xaxis_title="Skill",
        yaxis_title="Number of Candidates",
        height=400,
        width=800
    )
    
    st.plotly_chart(fig)

def plot_experience_distribution(candidates):
    """Plot the distribution of years of experience."""
    # Extract years of experience
    names = []
    years = []
    
    for _, candidate in candidates.iterrows():
        if candidate['nlp_results']:
            try:
                nlp_results = json.loads(candidate['nlp_results'])
                experience = nlp_results.get('experience_years', 0)
                
                if experience > 0:
                    names.append(candidate['name'])
                    years.append(experience)
            except:
                pass
    
    if not years:
        st.warning("No experience data available for visualization.")
        return
    
    # Create a DataFrame for plotting
    df = pd.DataFrame({
        'name': names,
        'years': years
    })
    
    # Sort by years of experience
    df = df.sort_values('years', ascending=False)
    
    # Create a horizontal bar chart using Plotly
    fig = px.bar(
        df,
        y='name',
        x='years',
        orientation='h',
        labels={'name': 'Candidate', 'years': 'Years of Experience'},
        title="Years of Experience by Candidate"
    )
    
    fig.update_layout(
        height=max(400, len(names) * 30),
        width=800,
        yaxis={'categoryorder': 'total ascending'}
    )
    
    st.plotly_chart(fig)

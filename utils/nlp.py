import spacy
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import re
import os
from pathlib import Path

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except:
    os.system("python -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# Load sentence transformer model
model_name = 'paraphrase-MiniLM-L6-v2'  # Smaller, faster model
model_cache_dir = Path("models")
model_cache_dir.mkdir(exist_ok=True)

# Initialize the model with caching
model = SentenceTransformer(model_name, cache_folder=str(model_cache_dir))

def preprocess_text(text):
    """Clean and preprocess text for NLP analysis."""
    # Convert to lowercase
    text = text.lower()
    
    # Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    
    # Remove email addresses
    text = re.sub(r'\S+@\S+', '', text)
    
    # Remove phone numbers
    text = re.sub(r'$$?\d{3}$$?[-.\s]?\d{3}[-.\s]?\d{4}', '', text)
    
    # Remove special characters and extra whitespace
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def extract_entities(text):
    """Extract named entities from text using spaCy."""
    doc = nlp(text)
    entities = {}
    
    for ent in doc.ents:
        if ent.label_ not in entities:
            entities[ent.label_] = []
        entities[ent.label_].append(ent.text)
    
    return entities

def extract_skills(text, skill_list):
    """Extract skills from text using a predefined skill list and NLP."""
    doc = nlp(text.lower())
    found_skills = set()
    
    # Direct matching
    for skill in skill_list:
        skill_lower = skill.lower()
        if skill_lower in text.lower():
            found_skills.add(skill)
    
    # Lemmatized matching
    doc_lemmas = {token.lemma_ for token in doc}
    for skill in skill_list:
        skill_doc = nlp(skill.lower())
        skill_lemmas = {token.lemma_ for token in skill_doc}
        # If all lemmas in the skill are found in the document
        if skill_lemmas.issubset(doc_lemmas):
            found_skills.add(skill)
    
    return list(found_skills)

def get_embedding(text):
    """Get embedding vector for text using sentence-transformers."""
    # Preprocess text
    text = preprocess_text(text)
    
    # Get embedding
    embedding = model.encode(text)
    
    return embedding

def semantic_similarity(text1, text2):
    """Calculate semantic similarity between two texts."""
    # Get embeddings
    embedding1 = get_embedding(text1)
    embedding2 = get_embedding(text2)
    
    # Reshape for cosine_similarity
    embedding1 = embedding1.reshape(1, -1)
    embedding2 = embedding2.reshape(1, -1)
    
    # Calculate cosine similarity
    similarity = cosine_similarity(embedding1, embedding2)[0][0]
    
    return similarity

def extract_education(text):
    """Extract education information using NLP."""
    education_keywords = [
        'bachelor', 'master', 'phd', 'doctorate', 'degree', 'diploma',
        'bsc', 'msc', 'ba', 'ma', 'mba', 'b.s.', 'm.s.', 'b.a.', 'm.a.',
        'university', 'college', 'institute', 'school'
    ]
    
    doc = nlp(text)
    education_info = []
    
    # Extract sentences containing education keywords
    for sent in doc.sents:
        sent_text = sent.text.lower()
        if any(keyword in sent_text for keyword in education_keywords):
            education_info.append(sent.text.strip())
    
    # Extract organizations that might be educational institutions
    for ent in doc.ents:
        if ent.label_ == 'ORG':
            context = text[max(0, ent.start_char - 50):min(len(text), ent.end_char + 50)]
            if any(keyword in context.lower() for keyword in education_keywords):
                if ent.text not in ' '.join(education_info):
                    education_info.append(f"{ent.text} (Educational Institution)")
    
    return education_info

def extract_experience_years(text):
    """Extract years of experience using NLP patterns."""
    # Patterns for years of experience
    patterns = [
        r'(\d+)\+?\s*years?\s*(?:of)?\s*experience',
        r'experience\s*(?:of)?\s*(\d+)\+?\s*years?',
        r'worked\s*(?:for)?\s*(\d+)\+?\s*years?',
        r'(\d+)\+?\s*years?\s*(?:in|at|with)',
    ]
    
    years = []
    for pattern in patterns:
        matches = re.findall(pattern, text.lower())
        years.extend([int(match) for match in matches])
    
    return max(years) if years else 0

def extract_job_titles(text):
    """Extract potential job titles using NLP."""
    common_titles = [
        'engineer', 'developer', 'manager', 'director', 'analyst',
        'specialist', 'consultant', 'coordinator', 'assistant',
        'designer', 'architect', 'administrator', 'supervisor',
        'lead', 'head', 'chief', 'officer', 'president', 'vp',
        'vice president', 'executive', 'founder', 'co-founder'
    ]
    
    doc = nlp(text)
    titles = []
    
    # Look for job title patterns
    for sent in doc.sents:
        sent_text = sent.text.lower()
        
        # Check for common title patterns
        for title in common_titles:
            # Look for patterns like "Senior Software Engineer" or "Marketing Manager"
            title_pattern = r'(?i)(?:^|\s)(?:senior|junior|principal|associate|assistant|lead|chief|head)?\s*(?:\w+\s+)*' + re.escape(title) + r'(?:\s+\w+)*(?:$|\s)'
            matches = re.findall(title_pattern, sent_text)
            titles.extend([match.strip() for match in matches if match.strip()])
    
    # Remove duplicates while preserving order
    unique_titles = []
    for title in titles:
        if title not in unique_titles:
            unique_titles.append(title)
    
    return unique_titles

def analyze_resume(resume_text, job_description, criteria_list):
    """
    Analyze a resume against a job description using NLP techniques.
    
    Args:
        resume_text: The full text of the resume
        job_description: The full text of the job description
        criteria_list: List of criteria to match against
        
    Returns:
        A dictionary containing analysis results
    """
    # Preprocess texts
    resume_clean = preprocess_text(resume_text)
    job_clean = preprocess_text(job_description)
    
    # Calculate overall semantic similarity
    overall_similarity = semantic_similarity(resume_clean, job_clean)
    
    # Extract skills (assuming criteria_list contains skills)
    skills = extract_skills(resume_clean, criteria_list)
    
    # Extract education information
    education = extract_education(resume_clean)
    
    # Extract years of experience
    experience_years = extract_experience_years(resume_clean)
    
    # Extract job titles
    job_titles = extract_job_titles(resume_clean)
    
    # Calculate criteria-specific similarities
    criteria_similarities = []
    for criterion in criteria_list:
        similarity = semantic_similarity(criterion, resume_clean)
        criteria_similarities.append({
            'criterion': criterion,
            'similarity': similarity
        })
    
    # Sort criteria similarities by score
    criteria_similarities.sort(key=lambda x: x['similarity'], reverse=True)
    
    # Prepare results
    results = {
        'overall_similarity': overall_similarity,
        'skills_matched': skills,
        'education': education,
        'experience_years': experience_years,
        'job_titles': job_titles,
        'criteria_matches': criteria_similarities
    }
    
    return results

import re
from utils.normalization import normalize_dates, normalize_skills
from utils.nlp import analyze_resume, semantic_similarity, extract_skills, extract_experience_years

def extract_keywords(text, keywords):
    """Extract keywords from text and return a dictionary of keyword counts."""
    text = text.lower()
    keyword_counts = {}
    
    for keyword in keywords:
        keyword_lower = keyword.lower()
        count = len(re.findall(r'\b' + re.escape(keyword_lower) + r'\b', text))
        if count > 0:
            keyword_counts[keyword] = count
    
    return keyword_counts

def extract_years_of_experience(text):
    """Extract years of experience from text."""
    return extract_experience_years(text)

def screen_candidate(candidate_data, criteria, job_description=""):
    """Screen a candidate against criteria and return a score and summary."""
    full_text = candidate_data['full_text']
    education_text = candidate_data['education']
    experience_text = candidate_data['experience']
    skills_text = candidate_data['skills']
    
    # Normalize dates and skills
    normalized_text = normalize_dates(full_text)
    normalized_text = normalize_skills(normalized_text)
    
    # Extract criteria texts
    criteria_texts = criteria['criterion'].tolist()
    
    # Use NLP to analyze the resume
    nlp_results = analyze_resume(full_text, job_description, criteria_texts)
    
    score = 0
    max_score = 0
    passed_criteria = []
    failed_required_criteria = []
    
    # Extract years of experience
    years_of_experience = nlp_results['experience_years']
    
    # Screen against each criterion
    for _, criterion in criteria.iterrows():
        criterion_text = criterion['criterion'].lower()
        weight = criterion['weight']
        required = criterion['required']
        
        max_score += weight
        
        # Find the similarity score for this criterion
        criterion_match = next((item for item in nlp_results['criteria_matches'] 
                               if item['criterion'].lower() == criterion_text), None)
        
        similarity_score = criterion_match['similarity'] if criterion_match else 0
        
        # Check if criterion is met (either by exact match or high similarity)
        if criterion_text in normalized_text.lower() or similarity_score > 0.7:
            score += weight
            passed_criteria.append({
                'criterion': criterion['criterion'],
                'similarity': similarity_score
            })
        elif required:
            failed_required_criteria.append({
                'criterion': criterion['criterion'],
                'similarity': similarity_score
            })
    
    # Add bonus for overall similarity
    overall_similarity_bonus = nlp_results['overall_similarity'] * 10
    score += overall_similarity_bonus
    max_score += 10  # Maximum possible bonus
    
    # Calculate percentage score
    percentage_score = (score / max_score * 100) if max_score > 0 else 0
    
    # Determine if candidate passed
    passed = len(failed_required_criteria) == 0 and percentage_score >= 50
    
    # Generate summary
    summary = []
    
    # Add overall match percentage
    summary.append(f"Overall match: {nlp_results['overall_similarity']*100:.1f}%")
    
    if years_of_experience > 0:
        summary.append(f"{years_of_experience} years of experience")
    
    # Add job titles if found
    if nlp_results['job_titles']:
        titles = nlp_results['job_titles'][:2]  # Take top 2 titles
        summary.append(f"Roles: {', '.join(titles)}")
    
    # Add top 3 passed criteria with highest similarity
    passed_criteria.sort(key=lambda x: x['similarity'], reverse=True)
    for criterion in passed_criteria[:3]:
        summary.append(f"Matches: {criterion['criterion']} ({criterion['similarity']*100:.1f}%)")
    
    # Add failed required criteria
    for criterion in failed_required_criteria:
        summary.append(f"Missing required: {criterion['criterion']} ({criterion['similarity']*100:.1f}%)")
    
    return {
        'score': percentage_score,
        'passed': passed,
        'summary': "\n".join(summary),
        'nlp_results': nlp_results
    }

import re
from dateutil import parser

def normalize_dates(text):
    """Normalize dates in text to YYYY-MM format."""
    # Find date patterns
    date_patterns = [
        r'\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)[.,]?\s+\d{4}\b',
        r'\b\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4}\b',
        r'\b\d{4}[/.-]\d{1,2}[/.-]\d{1,2}\b'
    ]
    
    normalized_text = text
    
    for pattern in date_patterns:
        dates = re.findall(pattern, text)
        for date_str in dates:
            try:
                parsed_date = parser.parse(date_str, fuzzy=True)
                normalized_date = parsed_date.strftime('%Y-%m')
                normalized_text = normalized_text.replace(date_str, normalized_date)
            except:
                pass
    
    return normalized_text

def normalize_skills(text):
    """Normalize skill names in text."""
    skill_mapping = {
        'ms office': 'microsoft office',
        'ms word': 'microsoft word',
        'ms excel': 'microsoft excel',
        'ms powerpoint': 'microsoft powerpoint',
        'react.js': 'react',
        'reactjs': 'react',
        'node.js': 'node',
        'nodejs': 'node',
        'vue.js': 'vue',
        'vuejs': 'vue',
        'angular.js': 'angular',
        'angularjs': 'angular',
        'js': 'javascript',
        'py': 'python',
        'c#': 'csharp',
        'c++': 'cplusplus',
        'aws': 'amazon web services',
        'gcp': 'google cloud platform',
        'azure': 'microsoft azure',
        'ml': 'machine learning',
        'ai': 'artificial intelligence',
        'dl': 'deep learning',
        'nlp': 'natural language processing',
        'cv': 'computer vision'
    }
    
    normalized_text = text.lower()
    
    for skill, normalized_skill in skill_mapping.items():
        normalized_text = re.sub(r'\b' + re.escape(skill) + r'\b', normalized_skill, normalized_text)
    
    return normalized_text

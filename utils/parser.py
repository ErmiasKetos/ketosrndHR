import pdfplumber
import re
import os
from pathlib import Path
import docx
import tempfile

# Regular expressions for extracting information
EMAIL_REGEX = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
PHONE_REGEX = r'(\+\d{1,3}[-.\s]?)?($$?\d{3}$$?[-.\s]?)?\d{3}[-.\s]?\d{4}'
EDUCATION_KEYWORDS = ['education', 'university', 'college', 'bachelor', 'master', 'phd', 'degree']
EXPERIENCE_KEYWORDS = ['experience', 'work', 'employment', 'job', 'career']
SKILLS_KEYWORDS = ['skills', 'technologies', 'tools', 'languages', 'frameworks']

def extract_text_from_pdf(file_path):
    """Extract text from a PDF file."""
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
    return text

def extract_text_from_docx(file_path):
    """Extract text from a DOCX file."""
    text = ""
    try:
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print(f"Error extracting text from DOCX: {e}")
    return text

def extract_text_from_file(file_path):
    """Extract text from a file based on its extension."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif ext == '.docx':
        return extract_text_from_docx(file_path)
    else:
        return ""

def extract_email(text):
    """Extract email from text."""
    emails = re.findall(EMAIL_REGEX, text)
    return emails[0] if emails else ""

def extract_phone(text):
    """Extract phone number from text."""
    phones = re.findall(PHONE_REGEX, text)
    if phones:
        # Join the parts of the phone number
        phone = ''.join(''.join(part) for part in phones[0] if part)
        return phone
    return ""

def extract_section(text, keywords, next_section_keywords=None):
    """Extract a section from text based on keywords."""
    lines = text.split('\n')
    section_text = ""
    in_section = False
    
    for line in lines:
        line_lower = line.lower()
        
        # Check if we're entering the section
        if not in_section:
            for keyword in keywords:
                if keyword in line_lower:
                    in_section = True
                    section_text += line + "\n"
                    break
        
        # Check if we're exiting the section
        elif next_section_keywords:
            should_exit = False
            for keyword in next_section_keywords:
                if keyword in line_lower:
                    should_exit = True
                    break
            
            if should_exit:
                break
            else:
                section_text += line + "\n"
        
        # If we're in the section and not checking for next section
        elif in_section:
            section_text += line + "\n"
    
    return section_text.strip()

def extract_name(text):
    """Extract name from the beginning of the resume."""
    lines = text.split('\n')
    for line in lines[:5]:  # Check first 5 lines
        line = line.strip()
        if line and not re.search(EMAIL_REGEX, line) and not re.search(PHONE_REGEX, line):
            # Exclude lines that are too long or contain common headers
            if len(line) < 50 and not any(keyword in line.lower() for keyword in ['resume', 'cv', 'curriculum']):
                return line
    return ""

def parse_resume(file_path):
    """Parse a resume file and extract relevant information."""
    # Extract text from file
    text = extract_text_from_file(file_path)
    if not text:
        return None
    
    # Extract basic information
    name = extract_name(text)
    email = extract_email(text)
    phone = extract_phone(text)
    
    # Extract sections
    all_keywords = EDUCATION_KEYWORDS + EXPERIENCE_KEYWORDS + SKILLS_KEYWORDS
    education = extract_section(text, EDUCATION_KEYWORDS, all_keywords)
    experience = extract_section(text, EXPERIENCE_KEYWORDS, all_keywords)
    skills = extract_section(text, SKILLS_KEYWORDS, all_keywords)
    
    # Return parsed data
    return {
        'name': name,
        'email': email,
        'phone': phone,
        'education': education,
        'experience': experience,
        'skills': skills,
        'full_text': text
    }

def save_uploaded_file(uploaded_file):
    """Save an uploaded file to a temporary location and return the path."""
    # Create a temporary file
    temp_dir = Path("temp_uploads")
    temp_dir.mkdir(exist_ok=True)
    
    file_path = temp_dir / uploaded_file.name
    
    # Write the file
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return str(file_path)

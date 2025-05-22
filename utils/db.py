import sqlite3
import os
from pathlib import Path
import pandas as pd

# Database file path
DB_PATH = Path("data/resume_screening.db")

# Ensure data directory exists
def initialize_database():
    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create tables if they don't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        created_by TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        active BOOLEAN DEFAULT 1
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS criteria (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id INTEGER NOT NULL,
        criterion TEXT NOT NULL,
        weight INTEGER DEFAULT 1,
        required BOOLEAN DEFAULT 0,
        FOREIGN KEY (job_id) REFERENCES jobs (id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS candidates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id INTEGER NOT NULL,
        name TEXT,
        email TEXT,
        phone TEXT,
        education TEXT,
        experience TEXT,
        skills TEXT,
        resume_path TEXT,
        score REAL DEFAULT 0,
        passed BOOLEAN DEFAULT 0,
        advanced BOOLEAN DEFAULT 0,
        summary TEXT,
        nlp_results TEXT,
        overall_similarity REAL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (job_id) REFERENCES jobs (id)
    )
    ''')
    
    # Commit changes and close connection
    conn.commit()
    conn.close()

# Function to save a job
def save_job(title, description, created_by):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO jobs (title, description, created_by) VALUES (?, ?, ?)",
        (title, description, created_by)
    )
    
    job_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    
    return job_id

# Function to save criteria
def save_criteria(job_id, criteria_list):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Delete existing criteria for this job
    cursor.execute("DELETE FROM criteria WHERE job_id = ?", (job_id,))
    
    # Insert new criteria
    for criterion in criteria_list:
        cursor.execute(
            "INSERT INTO criteria (job_id, criterion, weight, required) VALUES (?, ?, ?, ?)",
            (job_id, criterion['text'], criterion['weight'], criterion['required'])
        )
    
    conn.commit()
    conn.close()

# Function to get all jobs
def get_jobs(username=None):
    conn = sqlite3.connect(DB_PATH)
    
    query = "SELECT id, title, description, created_by, created_at, active FROM jobs"
    params = []
    
    if username:
        query += " WHERE created_by = ?"
        params.append(username)
    
    query += " ORDER BY created_at DESC"
    
    jobs = pd.read_sql_query(query, conn, params=params)
    
    conn.close()
    
    return jobs

# Function to get a specific job
def get_job(job_id):
    conn = sqlite3.connect(DB_PATH)
    
    job = pd.read_sql_query(
        "SELECT id, title, description, created_by, created_at, active FROM jobs WHERE id = ?",
        conn,
        params=[job_id]
    )
    
    conn.close()
    
    if job.empty:
        return None
    
    return job.iloc[0]

# Function to get criteria for a job
def get_criteria(job_id):
    conn = sqlite3.connect(DB_PATH)
    
    criteria = pd.read_sql_query(
        "SELECT id, criterion, weight, required FROM criteria WHERE job_id = ?",
        conn,
        params=[job_id]
    )
    
    conn.close()
    
    return criteria

# Function to save a candidate
def save_candidate(job_id, candidate_data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Convert nlp_results to JSON string if it exists
    nlp_results = None
    overall_similarity = 0
    if 'nlp_results' in candidate_data:
        import json
        nlp_results = json.dumps(candidate_data['nlp_results'])
        overall_similarity = candidate_data['nlp_results'].get('overall_similarity', 0)
    
    cursor.execute(
        """
        INSERT INTO candidates 
        (job_id, name, email, phone, education, experience, skills, resume_path, score, passed, summary, nlp_results, overall_similarity) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            job_id,
            candidate_data['name'],
            candidate_data['email'],
            candidate_data['phone'],
            candidate_data['education'],
            candidate_data['experience'],
            candidate_data['skills'],
            candidate_data['resume_path'],
            candidate_data['score'],
            candidate_data['passed'],
            candidate_data['summary'],
            nlp_results,
            overall_similarity
        )
    )
    
    candidate_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    
    return candidate_id

# Function to get candidates for a job
def get_candidates(job_id, passed_only=False):
    conn = sqlite3.connect(DB_PATH)
    
    query = "SELECT * FROM candidates WHERE job_id = ?"
    params = [job_id]
    
    if passed_only:
        query += " AND passed = 1"
    
    candidates = pd.read_sql_query(query, conn, params=params)
    
    conn.close()
    
    return candidates

# Function to update candidate status
def update_candidate_status(candidate_id, advanced):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE candidates SET advanced = ? WHERE id = ?",
        (advanced, candidate_id)
    )
    
    conn.commit()
    conn.close()

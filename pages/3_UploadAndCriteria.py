import streamlit as st
from zipfile import ZipFile
from io import BytesIO
from utils.parser import parse_resume
from utils.screening import score_candidate
from utils.db import get_db, Candidate, get_current_job


def app():
    st.title("📂 Upload Resumes & Initial Screening")
    
    # Ensure a job is selected
    job = get_current_job()
    if not job:
        st.warning("Please set up a job in the Job Setup page before uploading resumes.")
        return

    # File uploader: PDF, DOCX, or ZIP
    uploaded_files = st.file_uploader(
        "Upload Resumes (PDF/DOCX) or ZIP archive", 
        type=["pdf", "docx", "zip"], 
        accept_multiple_files=True
    )
    if not uploaded_files:
        return

    # Flatten files: extract ZIP archives
    resume_files = []
    for uploaded in uploaded_files:
        if uploaded.name.lower().endswith(".zip"):
            with ZipFile(BytesIO(uploaded.read())) as zipf:
                for name in zipf.namelist():
                    if name.lower().endswith((".pdf", ".docx")):
                        resume_files.append((name, BytesIO(zipf.read(name))))
        else:
            resume_files.append((uploaded.name, uploaded))

    st.info(f"{len(resume_files)} resume file(s) detected; ready to process.")

    if st.button("Run Initial Screening"):
        db = get_db()
        progress = st.progress(0)
        total = len(resume_files)
        for idx, (fname, fileobj) in enumerate(resume_files, start=1):
            # Parse resume fields
            fields = parse_resume(fileobj)
            # Score and summary based on job criteria
            score, summary = score_candidate(fields, job.criteria)
            # Determine pass/fail
            status = 'Pass' if score >= job.threshold else 'Fail'
            # Save to database
            Candidate.create(
                job_id=job.id,
                name=fields.get('name'),
                email=fields.get('email'),
                phone=fields.get('phone'),
                score=score,
                summary="\n".join(f"• {bullet}" for bullet in summary),
                status=status,
                raw_data=fields
            )
            progress.progress(idx/total)
        st.success("Screening complete! Navigate to the Screening Dashboard to review results.")


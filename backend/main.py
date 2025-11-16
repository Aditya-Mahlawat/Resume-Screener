import os
import tempfile
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any

# Import our custom logic
import parser
import matcher

# Initialize the FastAPI app
app = FastAPI(
    title="Automated Resume Screener API",
    description="API for parsing resumes and ranking them against job descriptions.",
    version="1.0.0"
)

# --- CORS Middleware ---
# This allows our frontend (running on http://localhost:3000)
# to make requests to our backend (running on http://localhost:8000)
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# --- Pydantic Models (for response structure) ---
class SkillCoverage(BaseModel):
    matched_skills: List[str]
    missing_skills: List[str]
    coverage_percentage: float

class RankResult(BaseModel):
    filename: str
    resume_skills: List[str]
    experience_years: float
    jd_skills: List[str]
    semantic_similarity: float
    skill_coverage: SkillCoverage
    final_score: float
    explanation: str

class ErrorResponse(BaseModel):
    detail: str


# --- API Endpoints ---
@app.get("/", summary="Health Check")
def read_root():
    """Root endpoint to check if the API is running."""
    return {"status": "ok", "message": "Resume Screener API is running!"}

@app.post(
    "/rank", 
    response_model=RankResult,
    summary="Parse, Score, and Rank a Resume",
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def rank_resume(
    job_description: str = Form(..., description="The full text of the job description."),
    resume_file: UploadFile = File(..., description="The candidate's resume file (PDF or DOCX).")
):
    """
    This is the main endpoint. It performs the full pipeline:
    1.  Receives a job description (text) and a resume (file).
    2.  Saves the resume to a temporary file.
    3.  Parses the resume to extract text, skills, and experience.
    4.  Parses the JD to extract required skills.
    5.  Calculates semantic similarity between the two.
    6.  Calculates skill coverage.
    7.  Computes a final weighted score.
    8.  Returns all data as a JSON response.
    """
    
    # Check for ML model
    if matcher.MODEL is None:
        raise HTTPException(status_code=500, detail="ML Model is not loaded. Cannot process request.")

    # 1. Save the uploaded file to a temporary location
    try:
        # Use a temporary file to save the upload
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(resume_file.filename)[1]) as temp_file:
            temp_file.write(await resume_file.read())
            temp_file_path = temp_file.name
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving temporary file: {e}")

    try:
        # 2. Parse the resume
        resume_data = parser.parse_resume(temp_file_path)
        if "error" in resume_data:
            raise HTTPException(status_code=400, detail=f"Error parsing resume: {resume_data['error']}")
        
        # 3. Parse the Job Description
        jd_skills = parser.parse_skills_from_jd(job_description)
        
        # 4. Calculate Semantic Similarity
        semantic_score = matcher.calculate_semantic_similarity(
            matcher.MODEL, 
            resume_data["raw_text"], 
            job_description
        )
        
        # 5. Calculate Skill Coverage
        skill_coverage_data = matcher.check_skill_coverage(
            resume_data["skills"], 
            jd_skills
        )
        
        # 6. Compute Final Score
        score_data = matcher.calculate_final_score(
            semantic_score,
            skill_coverage_data["coverage_percentage"]
        )
        
        # 7. Format the response
        response = RankResult(
            filename=resume_file.filename,
            resume_skills=resume_data["skills"],
            experience_years=resume_data["experience_years"],
            jd_skills=jd_skills,
            semantic_similarity=semantic_score,
            skill_coverage=SkillCoverage(**skill_coverage_data),
            final_score=score_data["final_score"],
            explanation=score_data["explanation"]
        )
        
        return response

    except Exception as e:
        # Catch-all for any other unexpected errors
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
    
    finally:
        # 8. Clean up the temporary file
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

# --- To run this app ---
# 1. Make sure you have all libraries from requirements.txt installed
# 2. Run in your terminal: uvicorn main:app --reload
# 3. Go to http://127.0.0.1:8000/docs to see the API documentation
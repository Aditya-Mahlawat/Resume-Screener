import re
from pdfminer.high_level import extract_text
import docx2txt
from rapidfuzz import process, fuzz
from typing import List, Dict, Any

# A more comprehensive list of skills. In a real project, this would be in a database.
SKILL_DATABASE = [
    'python', 'java', 'c++', 'c#', 'javascript', 'typescript', 'react', 'next.js',
    'angular', 'vue.js', 'node.js', 'express.js', 'django', 'flask', 'fastapi',
    'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'docker', 'kubernetes', 'aws',
    'azure', 'gcp', 'terraform', 'ansible', 'git', 'jira', 'scrum', 'agile',
    'machine learning', 'deep learning', 'pytorch', 'tensorflow', 'scikit-learn',
    'pandas', 'numpy', 'data analysis', 'data visualization', 'nlp', 'llm',
    'natural language processing', 'power bi', 'tableau', 'figma', 'adobe xd',
    'project management', 'product management', 'ui/ux design', 'team leadership'
]

def extract_text_from_pdf(file_path: str) -> str:
    """Extracts text content from a PDF file."""
    try:
        text = extract_text(file_path)
        return text.lower()
    except Exception as e:
        print(f"Error reading PDF {file_path}: {e}")
        return ""

def extract_text_from_docx(file_path: str) -> str:
    """Extracts text content from a DOCX file."""
    try:
        text = docx2txt.process(file_path)
        return text.lower()
    except Exception as e:
        print(f"Error reading DOCX {file_path}: {e}")
        return ""

def extract_skills(text: str, skill_list: List[str], threshold: int = 85) -> List[str]:
    """
    Extracts skills from text using fuzzy matching.
    We check for matches with a score > threshold to account for typos or variations.
    """
    found_skills = set()
    # Using rapidfuzz.process.extract to find all matches above the threshold
    # This is more efficient than looping and checking one by one
    matches = process.extract(text, skill_list, scorer=fuzz.PARTIAL_RATIO, limit=None, score_cutoff=threshold)
    
    for skill, score, _ in matches:
        found_skills.add(skill)
        
    return sorted(list(found_skills))

def extract_years_of_experience(text: str) -> float:
    """
    Extracts the maximum years of experience mentioned using regex.
    """
    # Regex to find patterns like "5 years", "5+ years", "5.5 years", "X yrs"
    patterns = [
        r'(\d+\.?\d*)\s*\+?\s*ye?a?rs?',
        r'(\d+\.?\d*)\s*\+?\s*yrs?'
    ]
    
    found_years = [0.0] # Start with 0
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            try:
                found_years.append(float(match))
            except ValueError:
                continue
                
    # Return the maximum experience found
    return max(found_years)

def parse_resume(file_path: str) -> Dict[str, Any]:
    """
    Main function to parse a resume file.
    Detects file type, extracts text, skills, and experience.
    """
    text = ""
    if file_path.endswith(".pdf"):
        text = extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        text = extract_text_from_docx(file_path)
    else:
        return {"error": "Unsupported file type"}

    if not text:
        return {"error": "Could not read text from file"}

    skills = extract_skills(text, SKILL_DATABASE)
    experience = extract_years_of_experience(text)
    
    return {
        "raw_text": text,
        "skills": skills,
        "experience_years": experience
    }

def parse_skills_from_jd(jd_text: str) -> List[str]:
    """
    Extracts required skills from a job description.
    Uses the same skill extraction logic as the resume parser.
    """
    jd_text_lower = jd_text.lower()
    skills = extract_skills(jd_text_lower, SKILL_DATABASE, threshold=90) # Higher threshold for JD
    return skills

# --- Test Block ---
if __name__ == "__main__":
    # To test this file, create a dummy file 'test.pdf' or 'test.docx' in this folder
    # Add some text like "I have 5 years of experience in Python and React."
    
    test_file = "test.pdf" # or 'test.docx'
    
    try:
        resume_data = parse_resume(test_file)
        if "error" in resume_data:
            print(f"Error: {resume_data['error']}")
        else:
            print("--- Resume Parsing Test ---")
            print(f"Skills Found: {resume_data['skills']}")
            print(f"Experience Found: {resume_data['experience_years']} years")
            # print(f"Raw Text: {resume_data['raw_text'][:500]}...") # Uncomment to see raw text

        print("\n--- JD Parsing Test ---")
        test_jd = "We need a senior developer with strong Python and AWS skills. React is a plus."
        jd_skills = parse_skills_from_jd(test_jd)
        print(f"JD Skills Found: {jd_skills}")

    except FileNotFoundError:
        print(f"Create a file named '{test_file}' to run the test.")
    except Exception as e:
        print(f"An error occurred: {e}")
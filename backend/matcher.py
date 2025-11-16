from sentence_transformers import SentenceTransformer, util
from typing import List, Dict, Any

# Load the model once when the module is imported.
# This saves time as we don't reload it for every request.
print("Loading ML model... (This may take a moment)")
try:
    MODEL = SentenceTransformer('all-MiniLM-L6-v2')
    print("ML model loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}")
    MODEL = None

def calculate_semantic_similarity(model: SentenceTransformer, text1: str, text2: str) -> float:
    """
    Calculates the cosine similarity score between two texts.
    """
    if model is None:
        print("Model is not loaded. Returning 0.0")
        return 0.0
        
    try:
        # Encode texts to get their embeddings (numerical representations)
        embedding1 = model.encode(text1, convert_to_tensor=True)
        embedding2 = model.encode(text2, convert_to_tensor=True)
        
        # Compute cosine similarity
        similarity = util.cos_sim(embedding1, embedding2)
        
        # The result is a tensor, get the float value
        return similarity.item()
    except Exception as e:
        print(f"Error calculating similarity: {e}")
        return 0.0

def check_skill_coverage(resume_skills: List[str], jd_skills: List[str]) -> Dict[str, Any]:
    """
    Checks which required skills (from JD) are present in the resume.
    """
    if not jd_skills:
        return {
            "matched_skills": [],
            "missing_skills": [],
            "coverage_percentage": 1.0  # If no skills are required, coverage is 100%
        }
        
    set_resume_skills = set(resume_skills)
    set_jd_skills = set(jd_skills)
    
    matched_skills = sorted(list(set_resume_skills.intersection(set_jd_skills)))
    missing_skills = sorted(list(set_jd_skills.difference(set_resume_skills)))
    
    coverage_percentage = len(matched_skills) / len(set_jd_skills)
    
    return {
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "coverage_percentage": coverage_percentage
    }

def calculate_final_score(
    semantic_score: float, 
    skill_coverage: float,
    weights: Dict[str, float] = None
) -> Dict[str, Any]:
    """
    Calculates a final weighted score and provides an explanation.
    """
    if weights is None:
        weights = {
            "semantic": 0.6,  # 60% weight on semantic text match
            "skill": 0.4      # 40% weight on must-have skill coverage
        }
        
    weighted_score = (weights["semantic"] * semantic_score) + (weights["skill"] * skill_coverage)
    
    # Provide a simple explanation
    explanation = (
        f"Score based on {weights['semantic']*100:.0f}% semantic similarity "
        f"({semantic_score:.2f}) and {weights['skill']*100:.0f}% skill coverage "
        f"({skill_coverage:.2f})."
    )
    
    return {
        "final_score": weighted_score,
        "explanation": explanation
    }

# --- Test Block ---
if __name__ == "__main__":
    if MODEL is None:
        print("Cannot run test: Model failed to load.")
    else:
        print("\n--- Matcher Test ---")
        
        # Test Data
        resume_text = "Experienced java developer with 5 years in backend systems. Also skilled in python and aws."
        resume_skills = ["java", "python", "aws"]
        
        jd_text = "Senior Java Developer wanted. Must know Java, AWS, and SQL. Python is a plus."
        jd_skills = ["java", "aws", "sql"]

        # 1. Test Semantic Similarity
        similarity = calculate_semantic_similarity(MODEL, resume_text, jd_text)
        print(f"Semantic Similarity: {similarity:.4f}")
        
        # 2. Test Skill Coverage
        coverage = check_skill_coverage(resume_skills, jd_skills)
        print(f"Skill Coverage: {coverage}")
        
        # 3. Test Final Score
        score_data = calculate_final_score(similarity, coverage["coverage_percentage"])
        print(f"Final Score Data: {score_data}")
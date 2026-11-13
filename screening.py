from database import save_candidate

def calculate_match_score(resume_text, required_skills):
    resume_text = resume_text.lower()

    matched_skills = []

    for skill in required_skills:
        if skill.lower() in resume_text:
            matched_skills.append(skill)

    if len(required_skills) == 0:
        return 0, matched_skills

    score = (len(matched_skills) / len(required_skills)) * 100

    return score, matched_skills



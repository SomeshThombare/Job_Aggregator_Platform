import re

KNOWN_SKILLS = ["Python", "Django", "Flask", "FastAPI", "React", "JavaScript", "TypeScript", "HTML", "CSS", "SQL", "MySQL", "PostgreSQL", "MongoDB", "Docker", "Kubernetes", "AWS", "Azure", "Git", "REST API", "Machine Learning", "AI", "LLM", "Pandas", "NumPy"]


def extract_skills(text: str) -> list[str]:
    lowered = (text or "").lower()
    return [skill for skill in KNOWN_SKILLS if re.search(rf"(?<!\w){re.escape(skill.lower())}(?!\w)", lowered)]


def score_job(job, roles: list[str], cities: list[str], profile_skills: list[str]) -> tuple[float, list[str]]:
    job_skills = {skill.lower() for skill in (job.technologies or job.required_skills or [])}
    user_skills = {skill.lower() for skill in profile_skills}
    common = job_skills & user_skills
    missing = sorted(skill for skill in (job.technologies or []) if skill.lower() not in user_skills)[:8]
    skill_score = 60 * len(common) / max(len(job_skills), 1)
    role_text = f"{job.job_title} {job.normalized_title}".lower()
    role_score = 25 if any(role.lower() in role_text or any(word in role_text for word in role.lower().split() if len(word) > 3) for role in roles) else 0
    city_text = (job.location or "").lower()
    location_score = 15 if job.remote_type == "Remote" or any(city.lower() in city_text for city in cities) else 0
    return min(round(skill_score + role_score + location_score), 100), missing


def refresh_match_scores(jobs, profile):
    for job in jobs:
        job.match_score, job.missing_skills = score_job(job, profile.target_roles, profile.target_cities, profile.skills)

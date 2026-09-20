import hashlib
import re

SKILL_ALIASES = {"postgres": "PostgreSQL", "postgres sql": "PostgreSQL", "react.js": "React", "reactjs": "React", "react js": "React", "js": "JavaScript", "javascript": "JavaScript", "rest": "REST API"}
ROLE_PATTERNS = [(r"django", "Django Developer"), (r"full[ -]?stack", "Full Stack Developer"), (r"python.*(backend|developer|engineer)|backend.*python", "Python Developer")]


def normalize_skill(skill: str) -> str:
    value = re.sub(r"\s+", " ", skill.strip().lower())
    return SKILL_ALIASES.get(value, " ".join(word.capitalize() for word in value.split()))


def normalize_title(title: str) -> str:
    lowered = title.lower()
    for pattern, category in ROLE_PATTERNS:
        if re.search(pattern, lowered):
            return category
    return title.strip()


def job_fingerprint(company: str, title: str, location: str) -> str:
    value = "|".join([company.strip().lower(), normalize_title(title).lower(), (location or "").strip().lower()])
    return hashlib.sha256(value.encode()).hexdigest()


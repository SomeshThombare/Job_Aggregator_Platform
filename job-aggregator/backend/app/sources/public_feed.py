from datetime import datetime, timezone
from app.sources.base import JobSource, SearchParams


class DemoPublicFeedSource(JobSource):
    """Safe development adapter. Replace its fixture with an allowed public API/RSS feed in production."""
    name = "Demo Public Feed"

    def fetch_jobs(self, search_params: SearchParams) -> list[dict]:
        return [
            {"id": "public-1001", "title": "Python Backend Developer", "company": "Acme Labs", "location": "Pune, Maharashtra", "remote_type": "Hybrid", "type": "Full Time", "experience": [0, 2], "skills": ["Python", "Django", "PostgreSQL", "REST API", "Docker"], "salary": [450000, 700000], "description": "Build reliable REST APIs with Django and PostgreSQL. Work with product and engineering teams.", "url": "https://example.com/jobs/public-1001"},
            {"id": "public-1002", "title": "Junior Full Stack Developer", "company": "Northstar Systems", "location": "Remote, India", "remote_type": "Remote", "type": "Full Time", "experience": [0, 1], "skills": ["Python", "React", "JavaScript", "MySQL", "Git"], "salary": [400000, 600000], "description": "Develop polished web experiences and Python services in a supportive remote team.", "url": "https://example.com/jobs/public-1002"},
            {"id": "public-1003", "title": "Django Developer Intern", "company": "OrbitWorks", "location": "Bangalore, Karnataka", "remote_type": "On-site", "type": "Internship", "experience": [0, 0], "skills": ["Python", "Django", "HTML", "CSS", "REST API"], "salary": [18000, 25000], "description": "Assist with Django feature development, API integration, testing, and documentation.", "url": "https://example.com/jobs/public-1003"},
        ]

    def parse_job(self, raw_job: dict) -> dict:
        return raw_job

    def normalize_job(self, job: dict) -> dict:
        return {**job, "source": self.name, "posted_date": datetime.now(timezone.utc)}


from datetime import datetime, timezone
from app.extensions import db


class JobSource(db.Model):
    __tablename__ = "job_sources"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    kind = db.Column(db.String(40), nullable=False, default="public_feed")
    enabled = db.Column(db.Boolean, nullable=False, default=True)
    rate_limit_seconds = db.Column(db.Integer, nullable=False, default=5)
    last_run_at = db.Column(db.DateTime(timezone=True))


class Job(db.Model):
    __tablename__ = "jobs"
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(100), nullable=False, index=True)
    source_job_id = db.Column(db.String(255))
    job_title = db.Column(db.String(255), nullable=False, index=True)
    normalized_title = db.Column(db.String(255), nullable=False)
    company_name = db.Column(db.String(255), nullable=False, index=True)
    company_url = db.Column(db.String(2048))
    job_description = db.Column(db.Text, nullable=False)
    clean_description = db.Column(db.Text)
    responsibilities = db.Column(db.Text)
    requirements = db.Column(db.Text)
    location = db.Column(db.String(255), index=True)
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    country = db.Column(db.String(100), default="India")
    remote_type = db.Column(db.String(30))
    employment_type = db.Column(db.String(50))
    experience_min = db.Column(db.Float)
    experience_max = db.Column(db.Float)
    salary_min = db.Column(db.Integer)
    salary_max = db.Column(db.Integer)
    salary_currency = db.Column(db.String(10), default="INR")
    openings = db.Column(db.Integer)
    education = db.Column(db.String(255))
    required_skills = db.Column(db.JSON, nullable=False, default=list)
    preferred_skills = db.Column(db.JSON, nullable=False, default=list)
    technologies = db.Column(db.JSON, nullable=False, default=list)
    posted_date = db.Column(db.DateTime(timezone=True))
    application_deadline = db.Column(db.DateTime(timezone=True))
    application_url = db.Column(db.String(2048), nullable=False)
    source_url = db.Column(db.String(2048), nullable=False)
    raw_job_data = db.Column(db.JSON, nullable=False, default=dict)
    status = db.Column(db.String(30), nullable=False, default="active")
    job_hash = db.Column(db.String(64), nullable=False, unique=True, index=True)
    duplicate_group_id = db.Column(db.String(64))
    match_score = db.Column(db.Float, default=0)
    missing_skills = db.Column(db.JSON, nullable=False, default=list)
    is_saved = db.Column(db.Boolean, nullable=False, default=False)
    is_ignored = db.Column(db.Boolean, nullable=False, default=False)
    scraped_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        def iso(value):
            return value.isoformat() if value else None
        return {
            "id": self.id, "source": self.source, "source_job_id": self.source_job_id,
            "job_title": self.job_title, "normalized_title": self.normalized_title,
            "company_name": self.company_name, "company_url": self.company_url,
            "job_description": self.job_description, "clean_description": self.clean_description,
            "responsibilities": self.responsibilities, "requirements": self.requirements,
            "location": self.location, "city": self.city, "state": self.state, "country": self.country,
            "remote_type": self.remote_type, "employment_type": self.employment_type,
            "experience_min": self.experience_min, "experience_max": self.experience_max,
            "salary_min": self.salary_min, "salary_max": self.salary_max, "salary_currency": self.salary_currency,
            "openings": self.openings, "education": self.education, "required_skills": self.required_skills,
            "preferred_skills": self.preferred_skills, "technologies": self.technologies,
            "posted_date": iso(self.posted_date), "application_deadline": iso(self.application_deadline),
            "application_url": self.application_url, "source_url": self.source_url, "status": self.status,
            "match_score": round(self.match_score or 0), "missing_skills": self.missing_skills,
            "is_saved": self.is_saved, "is_ignored": self.is_ignored, "scraped_at": iso(self.scraped_at),
        }


from app.extensions import db
from app.models.job import Job, JobSource
from app.services.normalization import job_fingerprint, normalize_skill, normalize_title
from app.sources.public_feed import DemoPublicFeedSource


def seed_demo_data():
    if Job.query.first():
        return
    source = DemoPublicFeedSource()
    db.session.add(JobSource(name=source.name, kind="development_fixture", enabled=True))
    for raw in source.fetch_jobs(None):
        item = source.normalize_job(source.parse_job(raw))
        skills = [normalize_skill(skill) for skill in item["skills"]]
        db.session.add(Job(source=item["source"], source_job_id=item["id"], job_title=item["title"], normalized_title=normalize_title(item["title"]), company_name=item["company"], job_description=item["description"], clean_description=item["description"], requirements="Required: " + ", ".join(skills), location=item["location"], city=item["location"].split(",")[0], remote_type=item["remote_type"], employment_type=item["type"], experience_min=item["experience"][0], experience_max=item["experience"][1], salary_min=item["salary"][0], salary_max=item["salary"][1], required_skills=skills, technologies=skills, posted_date=item["posted_date"], application_url=item["url"], source_url=item["url"], raw_job_data=raw, job_hash=job_fingerprint(item["company"], item["title"], item["location"]), match_score=88 if "Python" in skills else 76, missing_skills=["AWS"] if "Docker" in skills else ["Docker"]))
    db.session.commit()


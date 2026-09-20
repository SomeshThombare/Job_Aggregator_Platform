from datetime import datetime, timezone

from app.extensions import db
from app.models.job import Job, JobSource
from app.services.normalization import job_fingerprint, normalize_skill, normalize_title


def ingest_source(source, roles: list[str] | None = None) -> int:
    source_row = JobSource.query.filter_by(name=source.name).first()
    if not source_row:
        source_row = JobSource(name=source.name, kind="public_api", enabled=True, rate_limit_seconds=60)
        db.session.add(source_row)
    added = 0
    from app.sources.base import SearchParams
    for raw in source.fetch_jobs(SearchParams(roles=roles or [])):
        item = source.normalize_job(source.parse_job(raw))
        fingerprint = job_fingerprint(item["company"], item["title"], item["location"])
        if Job.query.filter_by(job_hash=fingerprint).first():
            continue
        skills = [normalize_skill(skill) for skill in item["skills"]]
        lower_text = f"{item['title']} {item['description']}".lower()
        score = 72 if "python" in lower_text else 55
        db.session.add(Job(
            source=item["source"], source_job_id=item["id"], job_title=item["title"],
            normalized_title=normalize_title(item["title"]), company_name=item["company"],
            job_description=item["description"], clean_description=item["description"],
            location=item["location"], city="Remote", remote_type=item["remote_type"],
            employment_type=item["type"], experience_min=item["experience"][0], experience_max=item["experience"][1],
            salary_min=item["salary"][0], salary_max=item["salary"][1], required_skills=skills,
            technologies=skills, posted_date=item["posted_date"], application_url=item["url"],
            source_url=item["url"], raw_job_data=item["raw"], job_hash=fingerprint,
            match_score=score, missing_skills=[]
        ))
        added += 1
    source_row.last_run_at = datetime.now(timezone.utc)
    db.session.commit()
    return added

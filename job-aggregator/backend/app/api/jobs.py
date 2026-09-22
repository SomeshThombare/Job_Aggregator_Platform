from collections import Counter
from flask import Blueprint, jsonify, request
import re
from sqlalchemy import and_, or_
from app.extensions import db
from app.models.job import Job, JobSource
from app.models.profile import Profile
from app.services.ingestion import ingest_source
from app.services.matching import extract_skills, refresh_match_scores
from app.sources.remotive import RemotiveSource

jobs_bp = Blueprint("jobs", __name__)


@jobs_bp.get("/health")
def health(): return {"status": "ok"}


def _items(value):
    if isinstance(value, list): return [str(item).strip() for item in value if str(item).strip()]
    return [item.strip() for item in str(value or "").split(",") if item.strip()]


def _profile():
    profile = db.session.get(Profile, 1)
    if not profile:
        profile = Profile(id=1)
        db.session.add(profile)
        db.session.commit()
    return profile


@jobs_bp.get("/profile")
def get_profile():
    return jsonify(_profile().to_dict())


@jobs_bp.put("/profile")
def update_profile():
    profile, payload = _profile(), request.get_json() or {}
    profile.target_roles = _items(payload.get("roles", profile.target_roles))
    profile.target_cities = _items(payload.get("cities", profile.target_cities))
    supplied_skills = _items(payload.get("skills", profile.skills))
    profile.skills = supplied_skills or extract_skills(profile.resume_text or "")
    refresh_match_scores(Job.query.all(), profile)
    db.session.commit()
    return jsonify(profile.to_dict())


@jobs_bp.post("/resume/upload")
def upload_resume():
    uploaded = request.files.get("resume")
    if not uploaded or not uploaded.filename:
        return jsonify({"error": "Choose a PDF or text resume first."}), 400
    if uploaded.filename.lower().endswith(".pdf"):
        from pypdf import PdfReader
        text = "\n".join(page.extract_text() or "" for page in PdfReader(uploaded).pages)
    elif uploaded.filename.lower().endswith(".txt"):
        text = uploaded.read().decode("utf-8", errors="ignore")
    else:
        return jsonify({"error": "Only PDF and TXT resumes are supported in Phase 1."}), 400
    if not text.strip():
        return jsonify({"error": "No readable text was found in this resume."}), 400
    profile = _profile()
    profile.resume_filename = uploaded.filename
    profile.resume_text = text
    profile.skills = extract_skills(text)
    refresh_match_scores(Job.query.all(), profile)
    db.session.commit()
    return jsonify(profile.to_dict())


@jobs_bp.get("/jobs")
def list_jobs():
    query = Job.query.filter_by(is_ignored=False)
    search = request.args.get("search", "").strip()
    source = request.args.get("source")
    location = request.args.get("location")
    if search:
        # Search concepts rather than requiring one exact phrase. For example,
        # "python fullstack developer" finds "Junior Full Stack Developer"
        # when Python appears in the job description.
        normalized_search = re.sub(r"full\s*-?\s*stack", "full stack", search.lower())
        ignored_words = {"developer", "engineer", "job", "jobs", "role", "position"}
        terms = [term for term in re.findall(r"[a-z0-9+#.]+", normalized_search) if term not in ignored_words]
        if terms:
            term_filters = []
            for term in terms:
                like = f"%{term}%"
                term_filters.append(or_(
                    Job.job_title.ilike(like), Job.company_name.ilike(like),
                    Job.location.ilike(like), Job.job_description.ilike(like),
                    Job.clean_description.ilike(like),
                ))
            query = query.filter(and_(*term_filters))
    if source and source != "All": query = query.filter_by(source=source)
    if location: query = query.filter(Job.location.ilike(f"%{location}%"))
    sort = request.args.get("sort", "match")
    order = Job.posted_date.desc() if sort == "recent" else Job.match_score.desc()
    page, per_page = max(request.args.get("page", 1, type=int), 1), min(max(request.args.get("per_page", 10, type=int), 1), 100)
    results = query.order_by(order).paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({"items": [job.to_dict() for job in results.items], "page": page, "per_page": per_page, "total": results.total, "pages": results.pages})


@jobs_bp.get("/jobs/<int:job_id>")
def get_job(job_id):
    return jsonify(Job.query.get_or_404(job_id).to_dict())


@jobs_bp.post("/jobs/<int:job_id>/save")
def save_job(job_id):
    job = Job.query.get_or_404(job_id); job.is_saved = not job.is_saved; db.session.commit()
    return jsonify(job.to_dict())


@jobs_bp.post("/jobs/<int:job_id>/ignore")
def ignore_job(job_id):
    job = Job.query.get_or_404(job_id); job.is_ignored = True; db.session.commit()
    return jsonify({"id": job.id, "is_ignored": True})


@jobs_bp.get("/sources")
def sources():
    return jsonify([{"id": source.id, "name": source.name, "kind": source.kind, "enabled": source.enabled, "last_run_at": source.last_run_at.isoformat() if source.last_run_at else None} for source in JobSource.query.all()])


@jobs_bp.post("/sources/remotive/refresh")
def refresh_remotive():
    payload = request.get_json(silent=True) or {}
    roles = payload.get("roles") or []
    try:
        added = ingest_source(RemotiveSource(), roles=roles)
    except Exception as error:
        return jsonify({"error": f"Could not contact Remotive: {error}"}), 502
    return jsonify({"source": "Remotive", "added": added})


@jobs_bp.post("/jobs/search")
def search_live_jobs():
    payload, profile = request.get_json() or {}, _profile()
    profile.target_roles = _items(payload.get("roles", profile.target_roles))
    profile.target_cities = _items(payload.get("cities", profile.target_cities))
    db.session.commit()
    try:
        added = ingest_source(RemotiveSource(), roles=profile.target_roles)
    except Exception as error:
        return jsonify({"error": f"Could not reach the permitted live source: {error}"}), 502
    refresh_match_scores(Job.query.all(), profile)
    db.session.commit()
    return jsonify({"added": added, "profile": profile.to_dict()})


@jobs_bp.get("/analytics")
def analytics():
    jobs = Job.query.filter_by(is_ignored=False).all()
    return jsonify({"total_jobs": len(jobs), "high_match": sum(job.match_score >= 80 for job in jobs), "saved": sum(job.is_saved for job in jobs), "by_source": Counter(job.source for job in jobs), "by_location": Counter(job.city for job in jobs), "by_technology": Counter(skill for job in jobs for skill in job.technologies)})

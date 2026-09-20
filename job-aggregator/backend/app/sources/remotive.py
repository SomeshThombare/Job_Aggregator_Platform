import html
import re
from datetime import datetime
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from app.sources.base import JobSource, SearchParams


def _plain_text(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value or "")
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


class RemotiveSource(JobSource):
    """Adapter for Remotive's documented public remote-jobs API."""
    name = "Remotive"
    endpoint = "https://remotive.com/api/remote-jobs"

    def fetch_jobs(self, search_params: SearchParams) -> list[dict]:
        terms = (search_params.roles if search_params else []) or []
        query = {"search": " ".join(terms)} if terms else {}
        request = Request(f"{self.endpoint}?{urlencode(query)}", headers={"User-Agent": "RoleRadar/0.1 (personal job search)"})
        with urlopen(request, timeout=20) as response:
            return __import__("json").loads(response.read().decode("utf-8")).get("jobs", [])

    def parse_job(self, raw_job: dict) -> dict:
        return raw_job

    def normalize_job(self, job: dict) -> dict:
        description = _plain_text(job.get("description", ""))
        tags = job.get("tags") or []
        published = job.get("publication_date")
        try:
            posted_date = datetime.fromisoformat(published.replace("Z", "+00:00")) if published else None
        except ValueError:
            posted_date = None
        return {
            "source": self.name, "id": str(job.get("id")), "title": job.get("title", "Untitled role"),
            "company": job.get("company_name", "Unknown company"), "location": job.get("candidate_required_location", "Remote"),
            "remote_type": "Remote", "type": job.get("job_type") or "Not specified",
            "experience": [None, None], "skills": tags, "salary": [None, None],
            "description": description, "url": job.get("url", ""), "posted_date": posted_date,
            "raw": job,
        }

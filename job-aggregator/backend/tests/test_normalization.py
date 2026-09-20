from app.services.normalization import job_fingerprint, normalize_skill, normalize_title


def test_normalizes_aliases_and_titles():
    assert normalize_skill("ReactJS") == "React"
    assert normalize_skill("postgres") == "PostgreSQL"
    assert normalize_title("Senior Python Backend Engineer") == "Python Developer"
    assert job_fingerprint("Acme", "Python Developer", "Pune") == job_fingerprint("acme", "Python Backend Developer", "pune")

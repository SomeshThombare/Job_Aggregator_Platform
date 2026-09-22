from app.extensions import db


class Profile(db.Model):
    """Single-user profile for this personal job-search installation."""
    __tablename__ = "profiles"
    id = db.Column(db.Integer, primary_key=True)
    target_roles = db.Column(db.JSON, nullable=False, default=list)
    target_cities = db.Column(db.JSON, nullable=False, default=list)
    skills = db.Column(db.JSON, nullable=False, default=list)
    resume_filename = db.Column(db.String(255))
    resume_text = db.Column(db.Text)

    def to_dict(self):
        return {"target_roles": self.target_roles, "target_cities": self.target_cities,
                "skills": self.skills, "resume_filename": self.resume_filename,
                "has_resume": bool(self.resume_text)}

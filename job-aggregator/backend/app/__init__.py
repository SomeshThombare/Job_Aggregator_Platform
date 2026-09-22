from flask import Flask
from flask_cors import CORS

from app.config import Config
from app.extensions import db


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    CORS(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})
    db.init_app(app)

    from app.api.jobs import jobs_bp
    app.register_blueprint(jobs_bp, url_prefix="/api")

    with app.app_context():
        from app import models  # Import every model before creating tables.
        db.create_all()
        from app.services.seed import seed_demo_data
        seed_demo_data()

    return app

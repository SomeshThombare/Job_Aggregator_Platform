# RoleRadar — Job Aggregator (Phase 1)

A production-minded foundation for aggregating permitted job sources into one normalized job model. Phase 1 includes Flask, SQLAlchemy (PostgreSQL-ready), a React dashboard, source adapter contract, title/skill normalization, duplicate fingerprints, and a safe local demo public-feed adapter.

## Run locally

1. Backend: `cd backend`, create/activate a virtual environment, then `pip install -r requirements.txt` and `python run.py`.
2. Frontend: `cd frontend`, run `npm install` then `npm run dev`.
3. Open the URL Vite prints (normally `http://localhost:5173`).

The default database is SQLite for zero-setup development. Copy `.env.example` to `.env` and set `DATABASE_URL` to use PostgreSQL. `docker-compose.yml` starts PostgreSQL and Redis for later Celery work.

## Free deployment starter

Use a Render Static Site for `frontend` (`Build Command: npm install && npm run build`, `Publish Directory: dist`) and a Render Web Service for `backend` (`Build Command: pip install -r requirements.txt`, `Start Command: gunicorn run:app`). Set `VITE_API_URL` for the static site to `https://YOUR-BACKEND.onrender.com/api`, and set the backend `CORS_ORIGINS` to the static site's URL.

For persistent data, create a Supabase Postgres project and set the backend `DATABASE_URL` to its SQLAlchemy-compatible connection URL, such as `postgresql+psycopg://USER:PASSWORD@HOST:5432/postgres?sslmode=require`. Never use SQLite on a free Render web service: its local files are ephemeral.

## Compliance boundary

No job-board scraper is included. Add an adapter only after confirming the source's official API/feed or explicit permission, plus robots/terms and rate-limit constraints. The sample `DemoPublicFeedSource` is fixture-only and makes the dashboard usable immediately.

## Next phases

- Add migrations, accounts, profile/resume upload and explainable match scoring.
- Add only permitted API/RSS/company-career adapters with per-source limits and run logs.
- Add Celery/Redis scheduling, exports, alerts, application tracking, and semantic deduplication.

"""Vercel entry point — exposes the FastAPI app as a serverless function.

vercel.json rewrites every path here. The app itself is unchanged; only two things differ from Render:
  * the database lives in /tmp (the only writable path on Vercel) and resets on every cold start
  * tables + seed data are created at import time, because lifespan events are not guaranteed in serverless
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlmodel import Session  # noqa: E402

from app.db import create_db_and_tables, engine  # noqa: E402
from app.main import app  # noqa: E402,F401  (Vercel looks for a module-level `app`)
from app.seed import seed  # noqa: E402

create_db_and_tables()
with Session(engine) as _session:
    seed(_session)

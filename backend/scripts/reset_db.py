#!/usr/bin/env python3
"""Reset database: drop all tables, recreate, and re-seed demo data."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.session import engine, Base, SessionLocal
from app.db.seed import seed_if_empty
from sqlalchemy import text


def reset():
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Creating tables and seeding...")
    seed_if_empty()
    print("Database reset complete.")


if __name__ == "__main__":
    reset()

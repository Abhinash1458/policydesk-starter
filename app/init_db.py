"""Initialize the PolicyDesk database.

This script is safe to re-run: create_all only adds missing tables;
seed only fills empty tables.
"""

import sqlite3

from sqlmodel import Session

from app.db import DATABASE_URL, create_db_and_tables, engine
from app.seed import seed


def main():
    create_db_and_tables()

    with Session(engine) as session:
        seed(session)

    database_url = DATABASE_URL
    print(f"DATABASE_URL: {database_url}")

    if database_url.startswith("sqlite"):
        database_path = database_url.split("///", 1)[-1]

        with sqlite3.connect(database_path) as connection:
            tables = connection.execute(
                "SELECT name FROM sqlite_master "
                "WHERE type='table' ORDER BY name"
            ).fetchall()

            for (table_name,) in tables:
                row_count = connection.execute(
                    f'SELECT COUNT(*) FROM "{table_name}"'
                ).fetchone()[0]
                print(f"{table_name}: {row_count} rows")


if __name__ == "__main__":
    main()
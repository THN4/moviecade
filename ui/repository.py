"""Read-only queries for arcade rounds."""

from sqlalchemy import text


def _engine():
    # Import on demand so the UI can show a useful error if .env is incomplete.
    from script.db import engine

    return engine


def movie_count() -> int:
    with _engine().connect() as connection:
        return connection.scalar(text("SELECT count(*) FROM fact_movies"))


def box_office_pair():
    with _engine().connect() as connection:
        first = connection.execute(text("""
            SELECT movie_id, title, revenue, poster_path
            FROM fact_movies
            WHERE revenue > 0 AND poster_path IS NOT NULL AND poster_path <> ''
            ORDER BY random()
            LIMIT 1
        """)).mappings().first()
        if not first:
            return None
        second = connection.execute(text("""
            SELECT movie_id, title, revenue, poster_path
            FROM fact_movies
            WHERE revenue > 0 AND poster_path IS NOT NULL AND poster_path <> ''
              AND movie_id <> :movie_id
              AND revenue <> :revenue
            ORDER BY random()
            LIMIT 1
        """), {"movie_id": first["movie_id"], "revenue": first["revenue"]}).mappings().first()
    return (dict(first), dict(second)) if second else None


def poster_movie(exclude_id=None):
    with _engine().connect() as connection:
        row = connection.execute(text("""
            SELECT movie_id, title, poster_path
            FROM fact_movies
            WHERE poster_path IS NOT NULL AND poster_path <> ''
              AND (CAST(:exclude_id AS INTEGER) IS NULL OR movie_id <> :exclude_id)
            ORDER BY random()
            LIMIT 1
        """), {"exclude_id": exclude_id}).mappings().first()
    return dict(row) if row else None


def detective_movie(exclude_id=None):
    with _engine().connect() as connection:
        row = connection.execute(text("""
            SELECT m.movie_id, m.title, m.overview, m.poster_path,
                   array_agg(DISTINCT g.name ORDER BY g.name) AS genres,
                   array_agg(DISTINCT c.name ORDER BY c.name) AS companies
            FROM fact_movies AS m
            JOIN bridge_movie_genres AS mg ON mg.movie_id = m.movie_id
            JOIN dim_genres AS g ON g.genre_id = mg.genre_id
            JOIN bridge_movie_companies AS mc ON mc.movie_id = m.movie_id
            JOIN dim_companies AS c ON c.company_id = mc.company_id
            WHERE m.overview IS NOT NULL AND btrim(m.overview) <> ''
              AND m.poster_path IS NOT NULL AND m.poster_path <> ''
              AND (CAST(:exclude_id AS INTEGER) IS NULL OR m.movie_id <> :exclude_id)
            GROUP BY m.movie_id, m.title, m.overview, m.poster_path
            ORDER BY random()
            LIMIT 1
        """), {"exclude_id": exclude_id}).mappings().first()
    return dict(row) if row else None

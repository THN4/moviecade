"""Movie titles offered as answers in the arcade."""

from sqlalchemy import text


def movie_titles() -> list[str]:
    from script.db import engine

    with engine.connect() as connection:
        return list(connection.scalars(text("""
            SELECT DISTINCT title FROM fact_movies ORDER BY title
        """)))

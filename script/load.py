import pandas as pd
from sqlalchemy import text
from script.db import engine


def load_tmdb_data(
    df_fact_movies: pd.DataFrame,
    df_dim_genres: pd.DataFrame,
    df_dim_companies: pd.DataFrame,
    df_bridge_genres: pd.DataFrame,
    df_bridge_companies: pd.DataFrame,
) -> None:

    FACT_MOVIES_UPSERT = text("""
        INSERT INTO fact_movies (
            movie_id, title, release_year, revenue, budget, overview,
            poster_path, backdrop_path, vote_average
        )
        VALUES (
            :movie_id, :title, :release_year, :revenue, :budget, :overview,
            :poster_path, :backdrop_path, :vote_average
        )
        ON CONFLICT (movie_id) DO UPDATE SET
            title = EXCLUDED.title,
            release_year = EXCLUDED.release_year,
            revenue = EXCLUDED.revenue,
            budget = EXCLUDED.budget,
            overview = EXCLUDED.overview,
            poster_path = EXCLUDED.poster_path,
            backdrop_path = EXCLUDED.backdrop_path,
            vote_average = EXCLUDED.vote_average,
            loaded_at = NOW();
        """)

    DIM_GENRES_UPSERT = text("""
        INSERT INTO dim_genres (genre_id, name)
        VALUES (:genre_id, :name)
        ON CONFLICT (genre_id) DO UPDATE SET
            name = EXCLUDED.name;
        """)

    DIM_COMPANIES_UPSERT = text("""
        INSERT INTO dim_companies (company_id, name)
        VALUES (:company_id, :name)
        ON CONFLICT (company_id) DO UPDATE SET
            name = EXCLUDED.name;
        """)

    BRIDGE_MOVIE_GENRES_UPSERT = text("""
        INSERT INTO bridge_movie_genres (movie_id, genre_id)
        VALUES (:movie_id, :genre_id)
        ON CONFLICT (movie_id, genre_id) DO NOTHING;
        """)

    BRIDGE_MOVIE_COMPANIES_UPSERT = text("""
        INSERT INTO bridge_movie_companies (movie_id, company_id)
        VALUES (:movie_id, :company_id)
        ON CONFLICT (movie_id, company_id) DO NOTHING;
        """)

    fact_rows = df_fact_movies.to_dict(orient="records")
    genre_rows = df_dim_genres.to_dict(orient="records")
    company_rows = df_dim_companies.to_dict(orient="records")
    bridge_genre_rows = df_bridge_genres.to_dict(orient="records")
    bridge_company_rows = df_bridge_companies.to_dict(orient="records")

    with engine.begin() as conn:
        if fact_rows:
            conn.execute(FACT_MOVIES_UPSERT, fact_rows)
        if genre_rows:
            conn.execute(DIM_GENRES_UPSERT, genre_rows)
        if company_rows:
            conn.execute(DIM_COMPANIES_UPSERT, company_rows)
        if bridge_genre_rows:
            conn.execute(BRIDGE_MOVIE_GENRES_UPSERT, bridge_genre_rows)
        if bridge_company_rows:
            conn.execute(BRIDGE_MOVIE_COMPANIES_UPSERT, bridge_company_rows)

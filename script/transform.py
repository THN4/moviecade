import json
import pandas as pd
from pathlib import Path
from IPython.display import display
from script.config import RAW_MOVIES_DETAIL_PATH

def transform_tmdb_data():
    
    with open(RAW_MOVIES_DETAIL_PATH, "r", encoding="utf-8") as f:
        raw_movies = json.load(f)

    fact_list = []
    genres_dict = {}       
    companies_dict = {}    
    bridge_genres_list = []
    bridge_companies_list = []

    for movie in raw_movies:
        if movie.get("revenue", 0) <= 0 or movie.get("budget", 0) <= 0 or not movie.get("poster_path"):
            continue

        m_id = movie["id"]

        # 1. Fact Table (fact_movies)
        fact_list.append({
            "movie_id": m_id,
            "title": movie.get("title"),
            "release_year": int(movie["release_date"][:4]) if movie.get("release_date") else None,
            "revenue": movie.get("revenue"),
            "budget": movie.get("budget"),
            "overview": movie.get("overview"),
            "poster_path": movie.get("poster_path"),
            "backdrop_path": movie.get("backdrop_path"),
            "vote_average": movie.get("vote_average")
        })

        # 2. Dimension & Bridge Genres
        for g in movie.get("genres", []): # default is []
            genres_dict[g["id"]] = g["name"]
            bridge_genres_list.append({"movie_id": m_id, "genre_id": g["id"]})

        # 3. Dimension & Bridge Production Companies
        for c in movie.get("production_companies", []):
            companies_dict[c["id"]] = c["name"]
            bridge_companies_list.append({"movie_id": m_id, "company_id": c["id"]})

    df_fact_movies = pd.DataFrame(fact_list)
    df_dim_genres = pd.DataFrame([{"genre_id": k, "name": v} for k, v in genres_dict.items()])
    df_dim_companies = pd.DataFrame([{"company_id": k, "name": v} for k, v in companies_dict.items()])
    df_bridge_genres = pd.DataFrame(bridge_genres_list)
    df_bridge_companies = pd.DataFrame(bridge_companies_list)
    
    return df_fact_movies, df_dim_genres, df_dim_companies,df_bridge_genres, df_bridge_companies
    
if __name__ == "__main__":
    df_fact, df_genres, df_companies, df_b_genres, df_b_companies = transform_tmdb_data()
    print(f"Transform success -> fact_movies {len(df_fact)} rows")
    print(f"Transform success -> fact_movies {len(df_genres)} rows")
    print(f"Transform success -> fact_movies {len(df_companies)} rows")
    print(f"Transform success -> fact_movies {len(df_b_genres)} rows")
    print(f"Transform success -> fact_movies {len(df_b_companies)} rows")
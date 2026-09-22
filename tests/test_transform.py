import json
import pytest
from script.transform import transform_tmdb_data

def test_transform_filters_invalid_movies(tmp_path):
    # 1. Arrange
    fake_raw_data = [
        # Movie 1: perfect data
        {
            "id": 101,
            "title": "Good Movie",
            "revenue": 1000000,
            "budget": 500000,
            "poster_path": "/good1.jpg",
            "release_date": "2026-01-01",
            "genres": [{"id": 28, "name": "Action"}]
        },
        # Movie 2: revenue = 0
        {
            "id": 102,
            "title": "Zero Revenue Movie",
            "revenue": 0,
            "budget": 500000,
            "poster_path": "/bad1.jpg"
        },
        # Movie 3: no poster_path 
        {
            "id": 103,
            "title": "No Poster Movie",
            "revenue": 1000000,
            "budget": 500000,
            "poster_path": None
        },
        # Movie 4: budget = 0
        {
            "id": 104,
            "title": "Zero Budget Movie",
            "revenue": 10000000,
            "budget": 0,
            "poster_path": "/bad2.jpg"
        },
        # Movie 5: perfect data
        {
            "id": 105,
            "title": "Good Movie 2",
            "revenue": 4000000,
            "budget": 400000,
            "poster_path": "/good2.jpg",
            "release_date": "2026-01-01",
            "genres": [{"id": 29, "name": "Sci-Fi"}]
        },
    ]

    fake_json_file = tmp_path / "fake_movies_detail.json"
    fake_json_file.write_text(json.dumps(fake_raw_data), encoding="utf-8")

    # 2. Act
    df_fact, df_genres, df_companies, df_b_genres, df_b_companies = transform_tmdb_data(input_path=fake_json_file)

    # 3. Assert
    assert len(df_fact) == 2                     
    assert df_fact.iloc[0]["movie_id"] == 101      
    assert df_fact.iloc[4]["release_year"] == 2026  
    assert len(df_genres) == 2                    
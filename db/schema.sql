CREATE TABLE fact_movies (
    movie_id            INTEGER PRIMARY KEY,
    title               VARCHAR(255) NOT NULL,
    release_year        INTEGER,
    revenue             BIGINT NOT NULL,
    budget              BIGINT NOT NULL,
    overview            TEXT,          
    poster_path         VARCHAR(255),  
    backdrop_path       VARCHAR(255),
    vote_average        NUMERIC(3,1),
    loaded_at           TIMESTAMP DEFAULT NOW()
);

-- 2. Dimension Tables
CREATE TABLE dim_genres (
    genre_id            INTEGER PRIMARY KEY,
    name                VARCHAR(100) NOT NULL
);

CREATE TABLE dim_companies (
    company_id          INTEGER PRIMARY KEY,
    name                VARCHAR(255) NOT NULL
);

-- 3. Bridge Tables (Mapping Many-to-Many Relationships)
CREATE TABLE bridge_movie_genres (
    movie_id            INTEGER REFERENCES fact_movies(movie_id) ON DELETE CASCADE,
    genre_id            INTEGER REFERENCES dim_genres(genre_id) ON DELETE CASCADE,
    PRIMARY KEY (movie_id, genre_id)
);

CREATE TABLE bridge_movie_companies (
    movie_id            INTEGER REFERENCES fact_movies(movie_id) ON DELETE CASCADE,
    company_id          INTEGER REFERENCES dim_companies(company_id) ON DELETE CASCADE,
    PRIMARY KEY (movie_id, company_id)
);
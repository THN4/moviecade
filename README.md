# Moviecade


Moviecade is a local batch data engineering project that turns movie data from
TMDB into a PostgreSQL star schema. A small Streamlit arcade uses the resulting
tables for three movie guessing games. The main focus is the ETL process, data
modeling, and automated tests.

One modeled dataset feeds three different games: revenue comparisons, poster
recognition, and clues assembled from movie, genre, and company tables. This
lets the arcade demonstrate the usefulness of the data model beyond a single
report or chart.

![Moviecade home page with links to three movie trivia games](docs/images/home.png)

## Data flow

```text
TMDB Discover API ──> data/raw/movies.json
                              │ movie IDs
                              ▼
TMDB Movie Details API ──> data/raw/movies_detail.json
                              │
                              ▼
                       Python / pandas transform
                              │
                              ▼
                    PostgreSQL star schema
                              │
                              ▼
                       Streamlit arcade
```

The pipeline is run manually with `python -m script.main`. Each run calls TMDB
again and overwrites the local JSON files. These files are staging artifacts
for inspection and for rerunning the transform separately. They are excluded
from Git.

## ETL process

### 1. Extract

[`script/extract.py`](script/extract.py) fetches pages from TMDB's Discover API
and saves the results to `data/raw/movies.json`. It then requests details for
each movie ID using a thread pool (four workers by default) and writes
`data/raw/movies_detail.json`. The detail response supplies fields that the
games need, including revenue, budget, genres, production companies, overview,
and poster path. A rate limit response (`429`) is retried once after five
seconds; failed detail requests are skipped.

### 2. Transform

[`script/transform.py`](script/transform.py) reads the detailed JSON and
filters out movies with nonpositive revenue or budget, or without a poster.
It extracts the release year and splits nested genres and production companies
into five pandas DataFrames that match the database tables. Genre and company
IDs are collected into dimensions; movie-to-genre and movie-to-company pairs
become bridge rows.

### 3. Load

[`script/load.py`](script/load.py) loads all five DataFrames into PostgreSQL
inside one SQLAlchemy transaction (`engine.begin()`). Movies and dimensions use
`ON CONFLICT DO UPDATE`; bridge tables use `ON CONFLICT DO NOTHING`. A failure
during the load rolls back the transaction. The schema is defined in
[`db/schema.sql`](db/schema.sql), and [`script/main.py`](script/main.py) runs
the connection check, schema setup, extract, transform, and load in order.
Repeated loads update existing movie and dimension rows and ignore duplicate
bridge pairs. Bridge pairs that disappear from TMDB are not deleted by the
current load logic.

## Data model

| Table | Purpose |
| --- | --- |
| `fact_movies` | One row per movie: title, release year, revenue, budget, overview, poster path, and ratings |
| `dim_genres` | Unique genre IDs and names |
| `dim_companies` | Unique production company IDs and names |
| `bridge_movie_genres` | Many-to-many link between movies and genres |
| `bridge_movie_companies` | Many-to-many link between movies and companies |

The bridge tables let the arcade combine movie facts with genre and company
clues through SQL joins without storing repeated genre or company names in the
fact table.

| Game | Data used |
| --- | --- |
| Box Office Battle | `fact_movies.revenue`, title, and poster path |
| Guess the Poster | `fact_movies.poster_path` and title |
| Movie Detective | Movie facts joined through both bridge tables to genres and production companies |

### Arcade preview

**Box Office Battle:** two posters and movie titles are shown while the second
movie's revenue stays hidden until the player guesses.

![Box Office Battle showing two movie posters and a hidden revenue](docs/images/box_office.png)

**Guess the Poster:** the poster starts blurred and becomes clearer when the
player requests a hint or makes a wrong guess.

![Guess the Poster showing a blurred poster and movie title picker](docs/images/poster.png)

**Movie Detective:** genres, production companies, and plot details are
revealed in stages. The screenshot shows all three clues before the answer.

![Movie Detective showing genre, company, and plot clues](docs/images/detective.png)

## Project structure

```text
moviecade/
├── .github/workflows/ci.yml   # GitHub Actions unit-test workflow
├── .streamlit/config.toml     # Arcade theme
├── data/raw/                  # Local JSON staging (JSON files ignored by Git)
├── db/schema.sql              # PostgreSQL fact, dimension, and bridge tables
├── docs/                      # Arcade and database validation screenshots
│   ├── db/
│   └── images/
├── script/                    # Batch ETL
│   ├── config.py              # Environment variables and file paths
│   ├── db.py                  # SQLAlchemy engine and schema setup
│   ├── extract.py             # TMDB Discover and movie-detail requests
│   ├── transform.py           # Cleaning and five-table DataFrame split
│   ├── load.py                # Transactional upserts
│   └── main.py                # Manual pipeline entry point
├── tests/                     # Extract, transform, load, DB, and game-rule tests
├── ui/                        # Streamlit arcade
│   ├── app.py                 # Page registration
│   ├── repository.py          # Read-only queries for game rounds
│   ├── catalog.py             # Movie-title choices from PostgreSQL
│   ├── game_logic.py          # Answer rules
│   ├── images.py              # TMDB poster loading
│   ├── widgets.py             # Shared title picker
│   └── pages/                 # Home and three game pages
├── .env.example               # Local configuration template
├── docker-compose.yml         # PostgreSQL and optional pgAdmin
└── requirements.txt           # Python dependencies
```

## Data quality and testing

- Transform rules keep revenue and budget above zero and require a poster path.
- Primary and foreign keys in PostgreSQL protect table relationships.
- [`tests/`](tests/) covers API extraction with mocked responses, transform
  filtering, database setup, load statements and transaction errors, and game
  rules.
- The unit tests do not require a live TMDB API or PostgreSQL server; running
  the full ETL locally does.

### Validation snapshot

The supplied database snapshot contains 370 movies, 18 genres, 484 companies,
1,100 movie–genre links, and 1,117 movie–company links. These counts describe
one local load; later runs can produce different totals.

```sql
SELECT
  (SELECT COUNT(*) FROM fact_movies) AS movies,
  (SELECT COUNT(*) FROM dim_genres) AS genres,
  (SELECT COUNT(*) FROM dim_companies) AS companies,
  (SELECT COUNT(*) FROM bridge_movie_genres) AS movie_genres,
  (SELECT COUNT(*) FROM bridge_movie_companies) AS movie_companies;
```

![PostgreSQL row counts for the five star schema tables](docs/db/count.png)

The quality check below returns `0` in the snapshot, matching the filter rules
in the transform step.

```sql
SELECT COUNT(*) AS invalid_movies
FROM fact_movies
WHERE revenue <= 0
   OR budget <= 0
   OR poster_path IS NULL
   OR poster_path = '';
```

![PostgreSQL query showing zero movies with invalid revenue, budget, or poster path](docs/db/zero.png)

## Continuous integration with GitHub Actions

The [CI workflow](.github/workflows/ci.yml) runs on pushes and pull requests
targeting `develop` or `main`. GitHub Actions checks out the repository, sets
up Python 3.11 on Ubuntu, installs `requirements.txt`, and runs `pytest -v`.
The project workflow is to merge a feature branch into `develop`, then promote
the integrated work to `main` after the checks pass.

The tests mock TMDB responses and replace database connections with test
doubles. The workflow sets dummy `POSTGRES_*` values so SQLAlchemy can build a
valid connection URL when modules are imported; it does not start PostgreSQL
or load movie data. CI therefore checks extraction, transformation, loading,
and database code without requiring API credentials or a running database.
The full ETL run remains a separate local verification step.

## Run locally

Use Python 3.11 and Docker. The commands below use PowerShell from the project
root:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Set `TMDB_API_KEY` in `.env` and check its PostgreSQL settings. Then run:

```powershell
docker compose up -d postgres
python -m script.main --pages 20
pytest -v
streamlit run ui/app.py
```

`--pages` controls how many Discover API pages are fetched (default: 20).
The arcade offers Box Office Battle, Guess the Poster, and Movie Detective.
Poster images are requested from TMDB when the games run. Stop the local
database with `docker compose down`.

## Notes to expand later

- Document lessons learned and current limitations after final testing.

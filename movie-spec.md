# Moviecade — Project Guideline (Learning-oriented Spec)

> This document is a "map," not a "step-by-step manual" — it sets direction and boundaries. How you solve each problem is up to you to figure out and research.

---

## 1. Goal

- Build a simple and robust ETL pipeline: TMDB API → Python (Local JSON Staging) → PostgreSQL
- Main focus of this project: **automated testing (Pytest, Mocking), CI/CD (GitHub Actions), and Relational Data Modeling (Star Schema)**.
- Present the pipeline's output as a small **movie trivia arcade** — a handful of interactive guessing games — instead of a dashboard.

**Definition of "done":** the pipeline runs successfully, tests cover the important logic (without hitting the real API), CI passes on every push, and all games are playable end-to-end using real data from the database.

---

## 2. Scope

**In scope:**
- Batch ETL using Python.
- Saving raw data locally (`.json` files) during extraction to save API calls and facilitate testing.
- Dimensional modeling (Star Schema) implemented via Python data manipulation before loading.
- Testing at every stage of the pipeline using Pytest.
- CI via GitHub Actions.
- 2–3 small games that read from the PostgreSQL database using SQL JOINs.

**Out of scope (intentionally cut — don't sneak these in mid-project):**
- Formal EDA (Exploratory Data Analysis) branch — simple data profiling in notebooks during development is enough.
- Orchestration with Airflow (use simple manual runs or CLI).
- Real-time / streaming data.
- dbt (Data Build Tool) — transformations will be handled purely in Python.
- Complex business logic (inflation adjustment, currency conversion).

---

## 3. High-Level Architecture (Python ETL to Star Schema)

```text
TMDB API 
   │
   ▼
[Extract] → Save to `data/raw/movies.json` (Local Storage)
   │           ↑ (Pytest mocks API here)
   ▼
[Transform] ← Reads local JSON, cleans, and splits arrays into Fact/Dim/Bridge structures
   │           ↑ (Pytest tests transformation logic)
   ▼
[Load]      ← Multi-table inserts (Transactions)
   │
   ▼
PostgreSQL (Star Schema: Fact + Dims + Bridges)
   │
   ▼
[Arcade: Streamlit Games]
```

---

## 4. The Games (Moviecade Arcade)

The idea: one shared pipeline and one Star Schema database feed multiple interactive guessing games. Each game leverages different attributes of the dataset.

### Game 1 — Box Office Battle (ทายรายได้)
Two movies are shown side by side. The player must guess whether the second movie's worldwide revenue (`revenue`) is higher or lower than the first. Correct guesses build a streak.

### Game 2 — Guess the Poster (ทายภาพโปสเตอร์)
The game displays a movie poster (`poster_path`) that is initially heavily blurred or partially revealed. The player must guess the movie title. The image becomes clearer (or reveals more parts) after a wrong guess or by requesting a hint.

### Game 3 — The Movie Detective (ทายหนังจากคำใบ้)
The player must guess the movie title based on textual clues. The game progressively reveals information: starting with the genre combination (`genres`), then the production company (`production_companies`), and finally a snippet of the plot summary (`overview`).

---

## 5. Data Schema Design (PostgreSQL Star Schema)

To support the trivia games, `overview` has been added to the Fact table, and the database is structured using a Star Schema for Many-to-Many relationships.

```sql
-- 1. Fact Table (Core Movie Metrics & Info)
CREATE TABLE fact_movies (
    movie_id            INTEGER PRIMARY KEY,
    title               VARCHAR(255) NOT NULL,
    release_year        INTEGER,
    revenue             BIGINT NOT NULL,
    budget              BIGINT,
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
```

---

## 6. Git Branch Strategy (Development Workflow)

To practice clean software engineering, this project uses a structured branching model. 

- **`main`**: Production-ready code. Merges come only from `develop` and must pass CI.
- **`develop`**: The main integration branch for active development. Feature branches merge here first.

| Branch Name | Purpose / Task Description |
| :--- | :--- |
| **`feature/project-foundation`** | Initial repository setup, folder structure creation, Docker/DB initialization, and requirement files. |
| **`feature/extract`** | Writing Python logic to fetch data from TMDB API, handle rate limits, and save raw `.json` files locally. |
| **`feature/transform`** | Reading local `.json` files, cleaning missing values, and splitting data into Fact/Dim/Bridge data structures (DataFrames/Dicts). |
| **`feature/load`** | Connecting to PostgreSQL, handling transactional multi-table inserts, and implementing Upsert logic (`ON CONFLICT`). |
| **`feature/pytest-suite`** | Writing unit tests, mocking the API calls, and validating data transformations. |
| **`feature/arcade-ui`** | Building the Streamlit frontend, SQL JOIN queries, and game logic (blurring images, streaks). |
| **`docs/readme-updates`** | Updating project documentation, adding architecture diagrams, and configuring the CI/CD badge. |

**Workflow Rule:** Write code in a `feature/*` branch -> Push and open a Pull Request to `develop` -> GitHub Actions automatically runs Pytest -> Merge only when CI passes. 

---

## 7. "Must Have" Checklist (what, not how)

### Extract
- [ ] Successfully pulls movie data from the TMDB API (including the `overview` field).
- [ ] Handles API errors / slow responses without crashing (Rate Limit handling).
- [ ] Saves the raw data as a `.json` file in a local directory (e.g., `data/raw/`).
- [ ] Has tests covering the extract logic using Mock objects.

### Transform (Python)
- [ ] Reads data from the locally saved `.json` file.
- [ ] Filters out incomplete records (e.g., revenue = 0).
- [ ] Successfully splits nested JSON arrays into separate data structures ready for the Star Schema.
- [ ] Has at least one unit test per filtering/transformation rule.

### Load (Python to PostgreSQL)
- [ ] Data lands in PostgreSQL correctly across all 5 tables.
- [ ] Handles multi-table insertions safely (transaction blocks to ensure all-or-nothing inserts).
- [ ] Handles duplicate data correctly (Upsert logic).

### CI/CD & Version Control
- [ ] Follows the feature branch workflow defined above.
- [ ] All tests run automatically via GitHub Actions on every push/PR to `develop` and `main`.
- [ ] README shows a test-status badge.

### Arcade (Games)
- [ ] Each game reads from the PostgreSQL database using SQL `JOIN`s where necessary.
- [ ] Image processing (blurring/revealing) for Game 2 works smoothly in Streamlit.
- [ ] All 3 games are playable end-to-end without crashing.

---

## 8. Questions to Ask Yourself While Building

- How do you handle database transactions in Python when inserting into multiple tables? (If inserting into `fact_movies` succeeds but `bridge_movie_genres` fails, what happens?)
- For Game 2, should the image blurring logic happen on the fly in Python/Streamlit, or will you pre-process and store blurred images?
- For Game 3, how will you query the Database to fetch a movie along with its combined genres and companies efficiently?
- Which Pytest fixtures can you create to make testing the split-table Transform logic easier?

---

## 9. Rough Timeline (adjust as needed)

| Phase | Goal |
|---|---|
| 1 | Setup: `feature/project-foundation` (Folder structure, Database setup) |
| 2 | Extract: `feature/extract` (TMDB API to local `.json`) |
| 3 | Transform: `feature/transform` (Process local JSON, split into Star Schema structures) |
| 4 | Load & Test: `feature/load` and `feature/pytest-suite` (Upsert to DB, ensure test coverage) |
| 5 | Games: `feature/arcade-ui` (Build Games 1, 2, and 3 using JOIN queries) |
| 6 | Release: `docs/readme-updates` (Set up CI via GitHub Actions + finalize README), Merge to `main` |
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

RAW_DATA_DIR = BASE_DIR / "data" / "raw"
RAW_MOVIES_PATH = RAW_DATA_DIR / "movies.json"
RAW_MOVIES_DETAIL_PATH = RAW_DATA_DIR / "movies_detail.json"

# API Configuration
TMDB_API_BASE_URL = os.getenv(
    "TMDB_API_BASE_URL", 
    "https://api.themoviedb.org/3"
)

# TMDB Endpoints
TMDB_DISCOVER_URL = f"{TMDB_API_BASE_URL}/discover/movie"
TMDB_MOVIE_DETAIL_URL = f"{TMDB_API_BASE_URL}/movie"  # + /{movie_id}

# API Key
TMDB_API_KEY = os.getenv(
    "TMDB_API_KEY", 
    ""
)

# Header
DEFAULT_HEADERS = {
    "accept": "application/json",
    "Authorization": f"Bearer {TMDB_API_KEY}"
}

# API Default User Parameters
DEFAULT_API_PARAMS = {
    "language": "en-US",
    "include_adult": "false",
    "page": 1,
    "vote_count.gte": 100,
    "with_original_language": "en|ko|th|cn",
    # "sort_by": "primary_release_date.desc" 
}

# Database Configuration
POSTGRES_USER = os.getenv("POSTGRES_USER", "")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
POSTGRES_DB = os.getenv("POSTGRES_DB", "")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "")

DATABASE_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

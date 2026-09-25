import json
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from script.config import (
    TMDB_DISCOVER_URL,
    TMDB_MOVIE_DETAIL_URL,
    DEFAULT_HEADERS,
    DEFAULT_API_PARAMS,
    RAW_MOVIES_PATH,
    RAW_MOVIES_DETAIL_PATH,
)

def extract_tmdb_discover(total_pages: int = 20):
    params = DEFAULT_API_PARAMS.copy()
    all_movies = []

    for page in range(1, total_pages + 1):
        params["page"] = page
        response = requests.get(TMDB_DISCOVER_URL, params=params, headers=DEFAULT_HEADERS)

        if response.status_code == 200:
            data = response.json()
            all_movies.extend(data["results"])
            print(f"[Discover] Page {page}/{total_pages}: Can retrieved {len(data['results'])} films")
        else:
            raise Exception(f"[Discover] Failed at page {page}. HTTP {response.status_code}")

    with open(RAW_MOVIES_PATH, "w", encoding="utf-8") as f:
        json.dump(all_movies, f, indent=4, ensure_ascii=False)

    print(f"\nDiscover finished! total: {len(all_movies)} films → {RAW_MOVIES_PATH}")
    return all_movies

def fetch_single_movie_detail(movie_id: int):
    url = f"{TMDB_MOVIE_DETAIL_URL}/{movie_id}"
    try:
        response = requests.get(url, headers=DEFAULT_HEADERS, params={"language": "en-US"})
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            time.sleep(5)
            retry_res = requests.get(url, headers=DEFAULT_HEADERS, params={"language": "en-US"})
            return retry_res.json() if retry_res.status_code == 200 else None
    except Exception as e:
        print(f"Error fetching {movie_id}: {e}")
    return None

def extract_tmdb_detail(max_workers: int = 4):
    with open(RAW_MOVIES_PATH, "r", encoding="utf-8") as f:
        movies = json.load(f)

    movie_ids = [movie["id"] for movie in movies]
    total = len(movie_ids)
    print(f"[Detail] Start retrieved detail {total} films by {max_workers} Threads...")

    all_details = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_id = {executor.submit(fetch_single_movie_detail, m_id): m_id for m_id in movie_ids}
        
        for i, future in enumerate(as_completed(future_to_id), start=1):
            result = future.result()
            if result:
                all_details.append(result)
            
            if i % 50 == 0 or i == total:
                print(f"  Progress: {i}/{total} films ")

    with open(RAW_MOVIES_DETAIL_PATH, "w", encoding="utf-8") as f:
        json.dump(all_details, f, indent=4, ensure_ascii=False)

    print(f"\nDetail finished! success {len(all_details)}/{total} films → {RAW_MOVIES_DETAIL_PATH}")

    return all_details

# Local module testing block
if __name__ == "__main__":
    extract_tmdb_discover(total_pages=20)
    extract_tmdb_detail()
import argparse

from script.db import init_db_schema, test_connection
from script.extract import extract_tmdb_discover, extract_tmdb_detail
from script.load import load_tmdb_data
from script.transform import transform_tmdb_data


def run_pipeline(total_pages: int = 20) -> None:
    test_connection()
    init_db_schema()

    extract_tmdb_discover(total_pages=total_pages)
    extract_tmdb_detail()

    dataframes = transform_tmdb_data()
    table_names = (
        "fact_movies",
        "dim_genres",
        "dim_companies",
        "bridge_movie_genres",
        "bridge_movie_companies",
    )
    for table_name, dataframe in zip(table_names, dataframes):
        print(f"Transform success -> {table_name}: {len(dataframe)} rows")

    load_tmdb_data(*dataframes)
    print("Moviecade ETL pipeline completed successfully!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Moviecade ETL pipeline")
    parser.add_argument(
        "--pages",
        type=int,
        default=20,
        help="Number of TMDB discover pages to fetch (default: 20).",
    )
    args = parser.parse_args()
    if args.pages < 1:
        parser.error("--pages must be at least 1")

    run_pipeline(total_pages=args.pages)

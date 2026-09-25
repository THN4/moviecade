import pandas as pd
import pytest

from script.load import load_tmdb_data


class FakeTransaction:
    def __init__(self, connection):
        self.connection = connection
        self.exception_type = None

    def __enter__(self):
        return self.connection

    def __exit__(self, exc_type, exc_value, traceback):
        self.exception_type = exc_type
        return False


class FakeConnection:
    def __init__(self):
        self.executions = []

    def execute(self, statement, parameters=None):
        self.executions.append((str(statement), parameters))


class FakeEngine:
    def __init__(self, connection):
        self.transaction = FakeTransaction(connection)

    def begin(self):
        return self.transaction


@pytest.fixture
def movie_dataframes():
    return (
        pd.DataFrame([
            {
                "movie_id": 101,
                "title": "Good Movie",
                "release_year": 2026,
                "revenue": 1_000_000,
                "budget": 500_000,
                "overview": "A test movie.",
                "poster_path": "/poster.jpg",
                "backdrop_path": "/backdrop.jpg",
                "vote_average": 8.5,
            }
        ]),
        pd.DataFrame([{"genre_id": 28, "name": "Action"}]),
        pd.DataFrame([{"company_id": 1, "name": "Test Studio"}]),
        pd.DataFrame([{"movie_id": 101, "genre_id": 28}]),
        pd.DataFrame([{"movie_id": 101, "company_id": 1}]),
    )


def test_load_executes_all_five_table_statements(monkeypatch, movie_dataframes):
    connection = FakeConnection()
    fake_engine = FakeEngine(connection)
    monkeypatch.setattr("script.load.engine", fake_engine)

    load_tmdb_data(*movie_dataframes)

    statements = [statement for statement, _ in connection.executions]
    assert len(statements) == 5
    assert "INSERT INTO fact_movies" in statements[0]
    assert "INSERT INTO dim_genres" in statements[1]
    assert "INSERT INTO dim_companies" in statements[2]
    assert "INSERT INTO bridge_movie_genres" in statements[3]
    assert "INSERT INTO bridge_movie_companies" in statements[4]
    assert connection.executions[0][1][0]["movie_id"] == 101
    assert fake_engine.transaction.exception_type is None


def test_load_skips_empty_dataframes(monkeypatch):
    connection = FakeConnection()
    monkeypatch.setattr("script.load.engine", FakeEngine(connection))
    empty_dataframe = pd.DataFrame()

    load_tmdb_data(
        empty_dataframe,
        empty_dataframe,
        empty_dataframe,
        empty_dataframe,
        empty_dataframe,
    )

    assert connection.executions == []


def test_load_propagates_error_from_transaction(monkeypatch, movie_dataframes):
    class FailingConnection(FakeConnection):
        def execute(self, statement, parameters=None):
            super().execute(statement, parameters)
            if len(self.executions) == 4:
                raise RuntimeError("Bridge insert failed")

    connection = FailingConnection()
    fake_engine = FakeEngine(connection)
    monkeypatch.setattr("script.load.engine", fake_engine)

    with pytest.raises(RuntimeError, match="Bridge insert failed"):
        load_tmdb_data(*movie_dataframes)

    assert fake_engine.transaction.exception_type is RuntimeError

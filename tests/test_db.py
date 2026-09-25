import pytest

from script import db


class FakeConnection:
    def __init__(self):
        self.executions = []

    def execute(self, statement, parameters=None):
        self.executions.append((str(statement), parameters))


class FakeContext:
    def __init__(self, connection):
        self.connection = connection
        self.exception_type = None

    def __enter__(self):
        return self.connection

    def __exit__(self, exc_type, exc_value, traceback):
        self.exception_type = exc_type
        return False


class FakeEngine:
    def __init__(self, connection):
        self.connection_context = FakeContext(connection)
        self.transaction_context = FakeContext(connection)

    def connect(self):
        return self.connection_context

    def begin(self):
        return self.transaction_context


def test_connection_runs_select_one(monkeypatch):
    connection = FakeConnection()
    fake_engine = FakeEngine(connection)
    monkeypatch.setattr(db, "engine", fake_engine)

    db.test_connection()

    assert connection.executions == [("SELECT 1;", None)]
    assert fake_engine.connection_context.exception_type is None


def test_init_db_schema_executes_schema_sql(monkeypatch):
    connection = FakeConnection()
    fake_engine = FakeEngine(connection)
    monkeypatch.setattr(db, "engine", fake_engine)

    db.init_db_schema()

    assert len(connection.executions) == 1
    schema_sql = connection.executions[0][0]
    assert "CREATE TABLE IF NOT EXISTS fact_movies" in schema_sql
    assert "CREATE TABLE IF NOT EXISTS bridge_movie_companies" in schema_sql
    assert fake_engine.transaction_context.exception_type is None


def test_init_db_schema_raises_when_schema_file_is_missing(monkeypatch):
    class MissingPath:
        def __init__(self, *_):
            pass

        def resolve(self):
            return self

        @property
        def parent(self):
            return self

        def __truediv__(self, _):
            return self

        def exists(self):
            return False

        def __str__(self):
            return "missing-schema.sql"

    monkeypatch.setattr(db, "Path", MissingPath)

    with pytest.raises(FileNotFoundError, match="Schema SQL file not found"):
        db.init_db_schema()

import json
import pytest
from requests_mock import ANY
from script.extract import extract_tmdb_discover, extract_tmdb_detail


def test_extract_tmdb_discover_success(requests_mock, monkeypatch, tmp_path):
    # 1. Arrange
    fake_response = {
        "page": 1,
        "results": [
            {"id": 101, "title": "Mock Movie 1"},
            {"id": 102, "title": "Mock Movie 2"},
        ],
    }
    requests_mock.get(ANY, json=fake_response, status_code=200)

    fake_movies_path = tmp_path / "movies.json"
    monkeypatch.setattr("script.extract.RAW_MOVIES_PATH", fake_movies_path)

    # 2. Act
    result = extract_tmdb_discover(total_pages=1)

    # 3. Assert
    assert len(result) == 2
    assert result[0]["title"] == "Mock Movie 1"
    assert fake_movies_path.exists()


def test_extract_tmdb_discover_failure(requests_mock):
    # 1. Arrange
    requests_mock.get(ANY, status_code=500)

    # 2. Act & Assert
    with pytest.raises(Exception) as exc_info:
        extract_tmdb_discover(total_pages=1)

    assert "HTTP 500" in str(exc_info.value)


def test_extract_tmdb_detail_success(requests_mock, monkeypatch, tmp_path):
    # 1. Arrange
    fake_movies_path = tmp_path / "movies.json"
    fake_movies_path.write_text(json.dumps([{"id": 101, "title": "Mock Movie 1"}]), encoding="utf-8")
    monkeypatch.setattr("script.extract.RAW_MOVIES_PATH", fake_movies_path)

    fake_detail_path = tmp_path / "movies_detail.json"
    monkeypatch.setattr("script.extract.RAW_MOVIES_DETAIL_PATH", fake_detail_path)

    fake_detail_response = {
        "id": 101,
        "title": "Mock Movie 1",
        "revenue": 100000000,
        "budget": 50000000,
        "genres": [{"id": 28, "name": "Action"}],
    }
    requests_mock.get(ANY, json=fake_detail_response, status_code=200)

    # 2. Act
    result = extract_tmdb_detail()
    # 3. Assert
    assert len(result) == 1
    assert result[0]["revenue"] == 100000000
    assert fake_detail_path.exists()
    fake_movies_path.exists()

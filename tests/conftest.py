import sys
import os
import pytest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))


@pytest.fixture
def mock_cursor():
    """
    A fake database cursor.
    MagicMock() creates an object where every attribute and
    method call just works — returning another MagicMock.
    We then set specific return values for the methods we care about.
    """
    cursor = MagicMock()
    cursor.lastrowid           = 1     # pretend every INSERT gets ID = 1
    cursor.fetchone.return_value = None  # default: nothing found
    cursor.fetchall.return_value = []    # default: empty list
    return cursor


@pytest.fixture
def mock_connection(mock_cursor):
    """A fake MySQL connection that returns mock_cursor."""
    conn = MagicMock()
    conn.cursor.return_value       = mock_cursor
    conn.is_connected.return_value = True
    return conn


@pytest.fixture
def sample_event():
    """A realistic event dict — simulates one row from our JOIN query."""
    return {
        "event_id": 1, "season": 2024, "status": "played",
        "date_venue": "2024-01-03", "time_venue_utc": "00:00:00",
        "sport_name": "Football", "competition_name": "AFC Champions League",
        "stage_name": "ROUND OF 16", "stage_ordering": 4,
        "home_team": "Al Shabab", "home_abbr": "SHA", "home_country": "KSA",
        "away_team": "Nasaf",     "away_abbr": "NAS", "away_country": "UZB",
        "venue_name": None, "venue_city": None,
        "home_goals": 1, "away_goals": 2, "winner": "Nasaf",
    }


@pytest.fixture
def new_event_payload():
    """A valid POST body for creating a new event."""
    return {
        "season": 2024, "status": "scheduled",
        "date_venue": "2024-03-15", "time_venue_utc": "18:00:00",
        "sport_name": "Football", "competition_name": "Premier League",
        "competition_slug": "premier-league",
        "stage_name": "Matchday 28", "stage_ordering": 28,
        "home_team_name": "Liverpool", "away_team_name": "Arsenal",
    }


@pytest.fixture
def flask_app():
    """Flask app in testing mode — raises exceptions instead of showing error pages."""
    from app import create_app
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(flask_app):
    """
    Flask test client — lets us send fake HTTP requests without
    starting a real server.
    Usage: response = client.get("/events")
    """
    return flask_app.test_client()
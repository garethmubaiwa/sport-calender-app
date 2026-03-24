# tests/test_routes.py — Integration tests for HTTP routes
# We test: correct status codes, JSON structure, filter forwarding,
# validation (400 on missing fields), 404 on missing events, 500 on errors.

import json
import pytest
from unittest.mock import patch, MagicMock


def mock_service(events=None, event=None, new_id=1, sport_names=None, error=None):
    """
    Helper: builds a mock EventService instance with sensible defaults.
    Pass error=Exception("msg") to simulate a service failure.
    """
    svc = MagicMock()
    svc.get_events.return_value     = events      or []
    svc.get_event.return_value      = event
    svc.create_event.return_value   = new_id
    svc.get_sport_names.return_value = sport_names or []
    if error:
        svc.create_event.side_effect = error
    return svc

# GET /  — Homepage

class TestHomepage:

    def test_returns_200(self, client):
        with patch("routes.get_connection"), \
             patch("routes.EventService", return_value=mock_service()):
            assert client.get("/").status_code == 200

    def test_returns_html(self, client):
        with patch("routes.get_connection"), \
             patch("routes.EventService", return_value=mock_service()):
            assert "text/html" in client.get("/").content_type

    def test_sport_filter_passed_to_service(self, client):
        svc = mock_service()
        with patch("routes.get_connection"), \
             patch("routes.EventService", return_value=svc):
            client.get("/?sport=Football")
        svc.get_events.assert_called_once_with("Football", None)


# GET /events — JSON list

class TestGetEvents:

    def test_returns_200_and_list(self, client, sample_event):
        with patch("routes.get_connection"), \
             patch("routes.EventService", return_value=mock_service(events=[sample_event])):
            response = client.get("/events")
        assert response.status_code == 200
        assert isinstance(json.loads(response.data), list)

    def test_returns_empty_list_when_no_events(self, client):
        with patch("routes.get_connection"), \
             patch("routes.EventService", return_value=mock_service()):
            assert json.loads(client.get("/events").data) == []

    def test_event_has_required_fields(self, client, sample_event):
        with patch("routes.get_connection"), \
             patch("routes.EventService", return_value=mock_service(events=[sample_event])):
            data = json.loads(client.get("/events").data)
        event = data[0]
        for field in ["event_id", "status", "home_team", "away_team", "sport_name"]:
            assert field in event, f"Missing field: {field}"

    def test_filters_forwarded(self, client):
        svc = mock_service()
        with patch("routes.get_connection"), \
             patch("routes.EventService", return_value=svc):
            client.get("/events?sport=Football&date=2024-01-03")
        svc.get_events.assert_called_once_with("Football", "2024-01-03")


# GET /events/<id> — Single event

class TestGetEventById:

    def test_returns_200_when_found(self, client, sample_event):
        with patch("routes.get_connection"), \
             patch("routes.EventService", return_value=mock_service(event=sample_event)):
            assert client.get("/events/1").status_code == 200

    def test_returns_correct_data(self, client, sample_event):
        with patch("routes.get_connection"), \
             patch("routes.EventService", return_value=mock_service(event=sample_event)):
            data = json.loads(client.get("/events/1").data)
        assert data["home_team"]  == "Al Shabab"
        assert data["home_goals"] == 1

    def test_returns_404_when_not_found(self, client):
        with patch("routes.get_connection"), \
             patch("routes.EventService", return_value=mock_service(event=None)):
            assert client.get("/events/999").status_code == 404

    def test_404_body_has_error_key(self, client):
        with patch("routes.get_connection"), \
             patch("routes.EventService", return_value=mock_service(event=None)):
            data = json.loads(client.get("/events/999").data)
        assert "error" in data

# POST /events — Create
class TestCreateEvent:

    def test_returns_201_on_success(self, client, new_event_payload):
        with patch("routes.get_connection"), \
             patch("routes.EventService", return_value=mock_service(new_id=10)):
            r = client.post("/events", json=new_event_payload)
        assert r.status_code == 201

    def test_response_contains_event_id(self, client, new_event_payload):
        with patch("routes.get_connection"), \
             patch("routes.EventService", return_value=mock_service(new_id=42)):
            data = json.loads(client.post("/events", json=new_event_payload).data)
        assert data["event_id"] == 42

    def test_returns_400_when_field_missing(self, client):
        """Missing required field → 400, service must never be called."""
        svc = mock_service()
        incomplete = {"season": 2024, "status": "scheduled"}  # many fields missing
        with patch("routes.get_connection"), \
             patch("routes.EventService", return_value=svc):
            r = client.post("/events", json=incomplete)
        assert r.status_code == 400
        svc.create_event.assert_not_called()

    def test_400_body_names_missing_field(self, client):
        with patch("routes.get_connection"), \
             patch("routes.EventService", return_value=mock_service()):
            data = json.loads(client.post("/events", json={"season": 2024}).data)
        assert "Missing required field" in data["error"]

    def test_returns_500_when_service_raises(self, client, new_event_payload):
        """Service error (e.g. DB down) → 500, rollback already done by service."""
        with patch("routes.get_connection"), \
             patch("routes.EventService", return_value=mock_service(error=Exception("DB error"))):
            r = client.post("/events", json=new_event_payload)
        assert r.status_code == 500
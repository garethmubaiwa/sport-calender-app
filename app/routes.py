from flask import Blueprint, request, jsonify, render_template, current_app
from service import EventService
from database import get_db_connection, close_db_connection
from config import get_env_variable
bp = Blueprint("events", __name__)


def _make_service():
    """
    Opens a DB connection and returns (service, connection).
    We return the connection too so routes can close it in
    a finally block even if the service raises an exception.
    """
    
    config     = get_env_variable()
    connection = get_db_connection(config)
    service    = EventService(connection)  # type: ignore
    return service, connection

# get - homepage
@bp.route("/")
def index():
    service, conn = _make_service()
    try:
        sport = request.args.get("sport")
        date  = request.args.get("date")
        return render_template(
            "index.html",
            events=service.get_events(sport, date),
            sports=service.get_sport_names(),
            sport_filter=sport or "",
            date_filter=date  or "",
        )
    finally:
        close_db_connection(conn)

# get all events as json
@bp.route("/events", methods=["GET"])
def get_events():
    service, conn = _make_service()
    try:
        sport  = request.args.get("sport")
        date   = request.args.get("date")
        return jsonify(service.get_events(sport, date))
    finally:
        close_db_connection(conn)


# single event as json
@bp.route("/events/<int:event_id>", methods=["GET"])
def get_event(event_id: int):
    # <int:event_id>: Flask pulls the number from the URL and
    # converts it to an int before passing it to this function.
    service, conn = _make_service()
    try:
        event = service.get_event(event_id)
        if event is None:
            return jsonify({"error": "Event not found"}), 404  # 404 = Not Found
        return jsonify(event)
    finally:
        close_db_connection(conn)


# post events - create a new event
@bp.route("/events", methods=["POST"])
def create_event():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    # Validate required fields — this is an HTTP concern.
    # We check the request format here, before touching the service.
    required = [
        "season", "status", "date_venue",
        "sport_name", "competition_name",
        "stage_name", "stage_ordering",
        "home_team_name", "away_team_name",
    ]
    for field in required:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
            # 400 = Bad Request — the client sent incomplete data

    service, conn = _make_service()
    try:
        new_id = service.create_event(data)
        return jsonify({"message": "Event created", "event_id": new_id}), 201
        # 201 = Created — the correct HTTP status for a new resource
    except Exception as e:
        # Service already called rollback(). We just report the error.
        return jsonify({"error": str(e)}), 500  # 500 = Internal Server Error
    finally:
        close_db_connection(conn)

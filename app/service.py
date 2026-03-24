from mysql.connector.connection import MySQLConnection
from repository import Repository

class EventService:
    """
    Service layer for event-related operations. This is where we put business logic,
    and where we manage transactions if needed. The service layer is a good place to
    put any logic that involves multiple repository calls, or that needs to ensure consistency across multiple operations.
    """
    def __init__(self, connection: MySQLConnection):
        self._conn = connection
        self._repo = Repository(connection)

    def _serialise(self, row: dict) -> dict:
        """
        Serialises a database row dict into a JSON-serialisable dict.
        This is where we can convert datetime objects to strings, or do any other transformations needed for the API response.
        eg. if the database returns a datetime object for "date_venue", we can convert it to an ISO string here.
        """
        row = dict(row)
        row["date_venue"] = str(row["date_venue"]) if row.get("date_venue") else None
        row["time_venue_utc"] = str(row["time_venue_utc"]) if row.get("time_venue_utc") else None
        return row


    def get_events(self, sport: str | None, date: str | None) -> list[dict]:
        """Returns all events, optionally filtered, serialised for JSON."""
        rows = self._repo.get_all_events(sport, date)
        return [self._serialise(row) for row in rows]

    def get_event(self, event_id: int) -> dict | None:
        """Returns one event by ID, or None if not found."""
        row = self._repo.get_event_by_id(event_id)
        return self._serialise(row) if row else None

    def get_sport_names(self) -> list[str]:
        """Returns a plain list of sport name strings for the filter dropdown."""
        return [row["name"] for row in self._repo.get_all_sport_names()]
    

    def create_event(self, data: dict) -> int:
        """
        Creates an event and all its related data atomically.

        ACID — Atomicity explained step by step:
          All six steps below run on the same connection,
          inside one open transaction (autocommit=False).
          If step 4 fails, steps 1-3 are rolled back.
          The database is left exactly as it was before we started.

        Args:
            data: validated dict from the route layer.

        Returns:
            The new event_id.

        Raises:
            Exception: re-raised after rollback so the route
                       can return a 500 error to the client.
        """
        try:
            # Step 1 — Sport
            # "get or create": only insert if missing.
            # This prevents duplicate "Football" rows.
            sport_row  = self._repo.find_sport(data["sport_name"])
            sport_id   = sport_row["sport_id"] if sport_row else self._repo.create_sport(data["sport_name"])

            # Step 2 — Competition
            comp_slug  = data.get("competition_slug", data["competition_name"].lower().replace(" ", "-"))
            comp_row   = self._repo.find_competition(comp_slug)
            comp_id    = comp_row["competition_id"] if comp_row else self._repo.create_competition(data["competition_name"], comp_slug, sport_id)

            # Step 3 — Stage
            stage_row  = self._repo.find_stage(data["stage_name"], comp_id)
            stage_id   = stage_row["stage_id"] if stage_row else self._repo.create_stage(data["stage_name"], data["stage_ordering"], comp_id)

            # Step 4 — Home team
            home_row   = self._repo.find_team(data["home_team_name"])
            home_id    = home_row["team_id"] if home_row else self._repo.create_team(data["home_team_name"])

            # Step 5 — Away team
            away_row   = self._repo.find_team(data["away_team_name"])
            away_id    = away_row["team_id"] if away_row else self._repo.create_team(data["away_team_name"])

            # Step 6 — Event
            event_id = self._repo.create_event(
                data["season"], data["status"], data["date_venue"],
                data.get("time_venue_utc"),
                home_id, away_id, comp_id, stage_id
            )

            # COMMIT — all 6 steps succeeded, save everything to disk.
            # This is the ONLY place commit() is called in the whole app.
            # ACID Durability: after this line the data is permanent.
            self._conn.commit()
            return event_id

        except Exception:
            # ROLLBACK — something failed, undo every insert above.
            # ACID Atomicity: the database is back to its clean state.
            self._conn.rollback()
            raise  # re-raise so the route can return HTTP 500

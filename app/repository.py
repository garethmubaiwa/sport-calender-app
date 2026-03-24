from typing import cast, Sequence
from mysql.connector.connection import MySQLConnection

_EVENTS_QUERY = """
    SELECT
        e.event_id,
        e.season,
        e.status,
        e.date_venue,
        e.time_venue,
        s.name AS sport_name,
        c.name AS competition_name,
        st.name AS stage_name,
        st.ordering AS stage_ordering,
        ht.name AS home_team,
        ht.abbreviation AS home_abbr,
        ht.country_code AS home_country,
        at.name AS away_team,
        at.abbreviation AS away_abbr,
        at.country_code AS away_country,
        v.name AS venue_name,
        v.city AS venue_city,
        r.home_goals,
        r.away_goals,
        r.winner
    FROM event e
        JOIN  competition c  ON e._competition_id = c.competition_id
        JOIN  sport s        ON c._sport_id = s.sport_id
        JOIN  stage st       ON e._stage_id = st.stage_id
        LEFT JOIN team ht    ON e._home_team_id = ht.team_id
        LEFT JOIN team at    ON e._away_team_id = at.team_id
        LEFT JOIN venue v    ON e._venue_id = v.venue_id
        LEFT JOIN result r   ON e.event_id = r._event_id
"""

# JOIN  = both rows must exist (competition and stage always exist)
# LEFT JOIN = keep the event row even if the right side is NULL
#             (teams can be TBD, venue may be unknown, result = not played yet)

class Repository:
    """
    All database queries for sports calendar.

    This class is responsible for connecting to the database and executing queries.
    Receives a connection in the constructor, so it can be mocked in tests.
    Dependency Inversion Principle: the Repository does not create its own connection, it receives it from outside.

    Never commits or rolls back.
    
    """

    def __init__(self, connection: MySQLConnection):
        self.conn = connection
        self.cursor = self.conn.cursor(dictionary=True) # return rows as dicts instead of tuples

    # event reader methods
    def get_all_events(self, sport: str | None = None, date: str | None = None) -> list[dict]:
        """Returns all events, optionally filtered by sport and/or date.
        Sport is the sport name, e.g. "Football".
        Date is the date of the event, in YYYY-MM-DD format.
        """
        query      = _EVENTS_QUERY
        params     = []
        conditions = []

        if sport:
            conditions.append("s.name = %s")
            params.append(sport)
        if date:
            conditions.append("e.date_venue = %s")
            params.append(date)
        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY e.date_venue ASC, e.time_venue ASC"

        self.cursor.execute(query, params)
        return cast(list[dict], self.cursor.fetchall())

    def get_event_by_id(self, event_id: int) -> dict | None:
        """Returns one event row by primary key, or None."""
        self.cursor.execute(_EVENTS_QUERY + " WHERE e.event_id = %s", (event_id,))
        return cast(dict | None, self.cursor.fetchone())

    # event writer methods
    def create_event(self, season, status, name, date_venue, time_venue, home_team_id, away_team_id, competition_id, stage_id) -> int:
        """Inserts a new event row. Returns the new event_id."""
        self.cursor.execute(
            """
            INSERT INTO event
                (season, status, name, date_venue, time_venue,
                 _home_team_id, _away_team_id, _competition_id, _stage_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (season, status, name, date_venue, time_venue,
             home_team_id, away_team_id, competition_id, stage_id)
        )
        return cast(int, self.cursor.lastrowid)
    

    # sport, competition, stage, team writer and reader methods
    def get_all_sport_names(self) -> list[dict]:
        """Returns all distinct sport names, sorted alphabetically."""
        self.cursor.execute("SELECT DISTINCT name FROM sport ORDER BY name")
        return cast(list[dict], self.cursor.fetchall())

    def find_sport(self, name: str) -> dict | None:
        """Looks up a sport by name."""
        self.cursor.execute(
            "SELECT sport_id FROM sport WHERE name = %s LIMIT 1", (name,)
        )
        return cast(dict | None, self.cursor.fetchone())

    def create_sport(self, name: str) -> int:
        """Inserts a new sport. Returns sport_id."""
        self.cursor.execute("INSERT INTO sport (name) VALUES (%s)", (name,))
        return cast(int, self.cursor.lastrowid)

    def find_competition(self, slug: str) -> dict | None:
        """Looks up a competition by slug."""
        self.cursor.execute(
            "SELECT competition_id FROM competition WHERE slug = %s LIMIT 1", (slug,)
        )
        return cast(dict | None, self.cursor.fetchone())

    def create_competition(self, name: str, slug: str, sport_id: int) -> int:
        """Inserts a new competition. Returns competition_id."""
        self.cursor.execute(
            "INSERT INTO competition (name, slug, _sport_id) VALUES (%s, %s, %s)",
            (name, slug, sport_id)
        )
        return cast(int, self.cursor.lastrowid)

    def find_stage(self, name: str, competition_id: int) -> dict | None:
        """Looks up a stage by name within a competition."""
        self.cursor.execute(
            "SELECT stage_id FROM stage WHERE name = %s AND _competition_id = %s LIMIT 1",
            (name, competition_id)
        )
        return cast(dict | None, self.cursor.fetchone())

    def create_stage(self, name: str, ordering: int, competition_id: int) -> int:
        """Inserts a new stage. Returns stage_id."""
        self.cursor.execute(
            "INSERT INTO stage (name, ordering, _competition_id) VALUES (%s, %s, %s)",
            (name, ordering, competition_id)
        )
        return cast(int, self.cursor.lastrowid)

    def find_team(self, name: str) -> dict | None:
        """Looks up a team by name."""
        self.cursor.execute(
            "SELECT team_id FROM team WHERE name = %s LIMIT 1", (name,)
        )
        return cast(dict | None, self.cursor.fetchone())

    def create_team(self, name: str) -> int:
        """Inserts a new team with a name and slug. Returns team_id."""
        slug = name.lower().replace(" ", "-")
        self.cursor.execute(
            "INSERT INTO team (name, official_name, slug, abbreviation, country_code) VALUES (%s, %s, %s, %s, %s)",
            (name, name, slug, "", "")
        )
        return cast(int, self.cursor.lastrowid)
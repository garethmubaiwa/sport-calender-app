# Sports Event Calendar

A web sports event calendar that allows events to be added and categorized based on sports.

---

## Project Overview

The Sports Event Calendar allows users to view upcoming and past sports events, filter them by sport or date, and add new events through a web interface or API. It is built with a clean layered architecture following SOLID design principles and ACID database guarantees.

**Tech stack:**
- **Database:** MySQL (InnoDB)
- **Backend:** Python 3 with Flask
- **Frontend:** HTML, CSS, JavaScript (bootstrap 5 templates)
- **Tests:** pytest with mock objects 


## Database Model (ERD)

erDiagram
    SPORTS ||--o{ COMPETITIONS : "categorizes"
    SPORTS ||--o{ TEAMS : "categorizes"
    COMPETITIONS ||--o{ STAGES : "contains"
    STAGES ||--o{ EVENTS : "hosts"
    TEAMS ||--o{ EVENTS : "plays as home"
    TEAMS ||--o{ EVENTS : "plays as away"
    VENUES ||--o{ EVENTS : "locates"
    EVENTS ||--o| RESULTS : "has"

    SPORTS {
        int id PK
        string name
    }

    COMPETITIONS {
        int id PK
        int _sport_id FK
        string name
        string slug
    }

    STAGES {
        int id PK
        int _competition_id FK
        string name
        int ordering
    }

    TEAMS {
        int id PK
        int _sport_id FK
        string name
        string country
    }

    VENUES {
        int id PK
        string name
        string city
    }

    EVENTS {
        int id PK
        int _stage_id FK
        int _home_team_id FK
        int _away_team_id FK
        int _venue_id FK
        int season
        string status
        date date_venue
        time time_venue_utc
    }

    RESULTS {
        int id PK
        int _event_id FK
        int home_goals
        int away_goals
        string winner
    }

## Project Structure

sports-calendar/
├── .env
├── .gitignore
├── requirements.txt
├── db/
│   ├── schema.sql        - creates all 7 tables
│   └── seed.sql          - sample data from a provided JSON
├── app/
│   ├── app.py            - creates and wires the Flask application
│   ├── config.py         - reads .env
│   ├── database.py       - opens and closes MySQL connections
│   ├── repository.py     - all SQL queries
│   ├── service.py        - business logic and transaction management
│   ├── routes.py         - HTTP request and response handling
│   └── templates/
│       └── index.html    - HTML frontend
└── tests/
    ├── conftest.py       - shared test fixtures
    └── test_routes.py    - integration tests for HTTP endpoints



## Setup Instructions

### Prerequisites
- Python 3.10 or higher
- MySQL 8.0 or higher running locally

### Step 1 — Install Python packages
`bash`
pip install -r requirements.txt


### Step 2 — Create the database
Open your MySQL client and run:
sql
CREATE DATABASE sports_calendar;


### Step 3 — Create the tables
`bash`
mysql -u root -p sports_calendar < db/schema.sql


### Step 4 — Load the sample data
`bash`
mysql -u root -p sports_calendar < db/seed.sql

### Step 5 — Configure your credentials
`bash`
cp .env.example .env

Open `.env` and fill in your MySQL username and password. This file is listed in `.gitignore` and will never be committed to version control.

### Step 6 — Run the application
`bash`
cd app
python app.py


Open **http://localhost:5000** in your browser.

### Step 7 — Run the tests (no database needed)
`bash`
python -m pytest tests/ -v


All tests run entirely with mock objects — no MySQL connection is required.

---

## API Endpoints
 
| Method  | URL            | Description                |
|-------- |-----           |-------------               |
| GET     | `/`            |  HTML event calendar page  |
| GET     | `/events`      | All events as JSON         |
| GET     | `/events/<id>` | One event by ID as JSON    |
| POST    | `/events`      | Create a new event         |

### Filters
Both `/` and `/events` accept optional query parameters:
```
?sport=Football
?date=2024-01-03
?sport=Football&date=2024-01-03
```

### POST /events — example request body
```json
{
  "season":           2024,
  "status":           "scheduled",
  "date_venue":       "2024-03-15",
  "time_venue_utc":   "18:00:00",
  "sport_name":       "Football",
  "competition_name": "Premier League",
  "competition_slug": "premier-league",
  "stage_name":       "Matchday 28",
  "stage_ordering":   28,
  "home_team_name":   "Liverpool",
  "away_team_name":   "Arsenal"
}
```

### HTTP status codes used
| Code | Meaning | When returned |
|------|---------|---------------|
| 200 | OK | Successful GET |
| 201 | Created | Successful POST |
| 400 | Bad Request | Missing required field in request body |
| 404 | Not Found | Event ID does not exist |
| 500 | Internal Server Error | Unexpected database error |

---

## Database Design

The schema follows **Third Normal Form (3NF)**: every piece of data is stored exactly once. For example, a team's name and country code live only in the `team` table — not repeated on every event row.

### Tables

| Table          | Purpose                                                 |
|----------------|---------------------------------------------------------|
| `sport`        | Top-level category — Football, Ice Hockey, etc.         |
| `competition`  | A league or tournament, belongs to one sport            |
| `venue`        | A physical stadium (optional on events)                 |
| `team`         | A sports team, reused across many events                |
| `stage`        | A round within a competition — Round of 16, Final, etc. |
| `event`        | One match — the central table linking everything        |
| `result`       | The score for a played event (separate from event)      |

All tables use `ENGINE=InnoDB`, which is required for foreign key constraints and transaction support in MySQL.

Foreign key columns are named with a `_` prefix as required by the exercise (e.g. `_sport_id`, `_home_team_id`).

---

## SOLID and ACID Principles Applied

• Single Responsibility: Files are strictly segregated by concern (config.py for env vars, repository.py for SQL, service.py for business logic).

• Dependency Inversion: The database connection is injected into the repository and service layers, allowing for comprehensive unit testing using Mock objects without a live database.

• Consistency & Durability: All tables utilize the InnoDB engine, strictly enforcing foreign key constraints and guaranteeing transaction durability upon commit().

---


## Assumptions and Design Decisions

• During the development of this application, several architectural and design decisions were made to prioritize data integrity, code maintainability, and user experience:

• Transaction Boundaries (Atomicity): A core assumption was that an event cannot exist without its corresponding sport, competition, or teams. Therefore, the responsibility for committing transactions was explicitly placed in the Service layer, not the Repository. The creation of an event triggers up to six SQL INSERT statements; encapsulating this in a single connection ensures that if any step fails, a rollback() leaves the database in a perfectly clean state.

• Result State Separation: Instead of using nullable home_goals and away_goals columns on the event table, a dedicated result table was created. This enforces a cleaner domain model: a scheduled match simply has no row in the result table, eliminating the need to handle NULL score logic in the application layer.

• Handling Incomplete Data (TBD status): The provided JSON payload contained events (like Finals) where the home or away teams were not yet decided (null). The schema accounts for this by allowing _home_team_id, _away_team_id, and _venue_id to be nullable foreign keys.

• Efficient Data Retrieval vs. N+1 Queries:
To adhere to the requirement of avoiding SQL queries inside loops, the system relies on a single, comprehensive LEFT JOIN query in the repository. This trades a slightly larger payload footprint for a massive reduction in database round-trips, significantly improving backend latency.

• Frontend UI Framework: Given the time constraints of the assessment, I assumed that a clean, modern interface was desired but a heavy JavaScript framework (like React or Angular) would be over-engineered. I opted for Bootstrap 5 via CDN, allowing for a responsive, professional-grade UI without the overhead of a complex build pipeline.

• I chose to use Mermaid.js for the ERD to keep the documentation 'as code,' allowing the schema visualization to stay perfectly in sync with the repository's development history.

```NB: MySQL "InterfaceError: 2003"```
This occurs if the DB Port is passed as a string. The config.py uses int(os.getenv("DB_PORT")) to ensure type-safety.
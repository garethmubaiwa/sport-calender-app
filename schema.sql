CREATE TABLE IF NOT EXISTS sport(
    sport_id  INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS competition (
    competition_id  INT AUTO_INCREMENT PRIMARY KEY
    name VARCHAR(255) NOT NULL,
    sport_id INT,
    FOREIGN KEY (sport_id) REFERENCES sport(sport_id)
) ENGINE=InnoDB;

create table if not exists venue(
    venue_id int AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL, 
    city VARCHAR(255) NOT NULL,
    country VARCHAR(255) NOT NULL
) ENGINE=InnoDB;

create table if not exists team(
    team_id int AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    official_name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) NOT NULL,
    abbreviation VARCHAR(10),
    country_code VARCHAR(10) -- e.g., 'UZB' for Uzbekistan, 'KSA' for Saudi Arabia
) ENGINE=InnoDB;

create table if not exists stage(
    stage_id int AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    ordering INT,
    _competition_id INT,
    FOREIGN KEY (_competition_id) REFERENCES competition(competition_id) 
) ENGINE=InnoDB;

create table if not exists event(
    event_id int AUTO_INCREMENT PRIMARY KEY,
    season int NOT NULL,
    status VARCHAR(50) NOT NULL, -- e.g., 'scheduled', 'ongoing', 'completed'
    name VARCHAR(255) NOT NULL,
    date_venue date NOT NULL,
    time_venue time, 

    -- Foreign keys
    _home_team_id INT,
    _away_team_id INT,
    _competition_id INT,
    _venue_id INT,
    _stage_id INT

    FOREIGN KEY (_home_team_id) REFERENCES team(team_id),
    FOREIGN KEY (_away_team_id) REFERENCES team(team_id),
    FOREIGN KEY (_competition_id) REFERENCES competition(competition_id),
    FOREIGN KEY (_venue_id) REFERENCES venue(venue_id),
    FOREIGN KEY (_stage_id) REFERENCES stage(stage_id)

) ENGINE=InnoDB;

create table if not exists result(
    result_id int AUTO_INCREMENT PRIMARY KEY,
    home_goals INT,
    away_goals INT,
    winnner VARCHAR(50),

    -- Foreign key
    _event_id INT,
    FOREIGN KEY (_event_id) REFERENCES event(event_id)
) ENGINE=InnoDB;

create table if not exists goal(
    goal_id int AUTO_INCREMENT PRIMARY KEY,
    _event_id INT NOT NULL, 
    _team_id INT NOT NULL,
    player_name VARCHAR(255),
    minute INT,
    FOREIGN KEY (_event_id) REFERENCES event(event_id),
    FOREIGN KEY (_team_id) REFERENCES team(team_id)
) ENGINE=InnoDB;

create table if not exists card(
    card_id int AUTO_INCREMENT PRIMARY KEY,
    _event_id INT NOT NULL, 
    card_type VARCHAR(50) NOT NULL, -- e.g., 'yellow', 'red'
    player_name VARCHAR(255),
    minute INT,
    FOREIGN KEY (_event_id) REFERENCES event(event_id),
) ENGINE=InnoDB;



CREATE INDEX idx_sport_id ON events(_sport_id);
CREATE INDEX idx_competition_id ON events(_competition_id);
CREATE INDEX idx_stage_id ON events(_stage_id);
CREATE INDEX idx_venue_id ON events(_venue_id);
CREATE INDEX idx_home_team_id ON events(_home_team_id);
CREATE INDEX idx_away_team_id ON events(_away_team_id);
INSERT IGNORE INTO sport (name) VALUES ('Football');
INSERT IGNORE INTO sport (name) VALUES ('Ice Hockey');
 
INSERT IGNORE INTO competition (name, slug, _sport_id) VALUES (
    'AFC Champions League', 'afc-champions-league',
    (SELECT sport_id FROM sport WHERE name = 'Football')
);
INSERT IGNORE INTO competition (name, slug, _sport_id) VALUES (
    'Austrian Football League', 'austrian-football-league',
    (SELECT sport_id FROM sport WHERE name = 'Football')
);
INSERT IGNORE INTO competition (name, slug, _sport_id) VALUES (
    'Austrian Ice Hockey League', 'austrian-ice-hockey-league',
    (SELECT sport_id FROM sport WHERE name = 'Ice Hockey')
);
 
INSERT IGNORE INTO stage (name, ordering, _competition_id) VALUES ('ROUND OF 16', 4, (SELECT competition_id FROM competition WHERE slug = 'afc-champions-league'));
INSERT IGNORE INTO stage (name, ordering, _competition_id) VALUES ('FINAL',       7, (SELECT competition_id FROM competition WHERE slug = 'afc-champions-league'));
INSERT IGNORE INTO stage (name, ordering, _competition_id) VALUES ('Regular Season', 1, (SELECT competition_id FROM competition WHERE slug = 'austrian-football-league'));
INSERT IGNORE INTO stage (name, ordering, _competition_id) VALUES ('Regular Season', 1, (SELECT competition_id FROM competition WHERE slug = 'austrian-ice-hockey-league'));
 
INSERT IGNORE INTO venue (name, city, country) VALUES ('Red Bull Arena', 'Salzburg',   'Austria');
INSERT IGNORE INTO venue (name, city, country) VALUES ('KAC Arena',      'Klagenfurt', 'Austria');
 
INSERT IGNORE INTO team (name, official_name, slug, abbreviation, country_code) VALUES ('Al Shabab', 'Al Shabab FC', 'al-shabab-fc', 'SHA', 'KSA');
INSERT IGNORE INTO team (name, official_name, slug, abbreviation, country_code) VALUES ('Nasaf', 'FC Nasaf', 'fc-nasaf-qarshi', 'NAS', 'UZB');
INSERT IGNORE INTO team (name, official_name, slug, abbreviation, country_code) VALUES ('Al Hilal', 'Al Hilal Saudi FC', 'al-hilal-saudi-fc', 'HIL', 'KSA');
INSERT IGNORE INTO team (name, official_name, slug, abbreviation, country_code) VALUES ('Shabab Al Ahli', 'SHABAB AL AHLI DUBAI', 'shabab-al-ahli-club', 'SAH', 'UAE');
 
-- AFC Match 1: Al Shabab vs Nasaf (played)
INSERT INTO event (season, status, date_venue, time_venue_utc, _home_team_id, _away_team_id, _competition_id, _stage_id) VALUES (
    2024, 'played', '2024-01-03', '00:00:00',
    (SELECT team_id FROM team WHERE slug = 'al-shabab-fc'),
    (SELECT team_id FROM team WHERE slug = 'fc-nasaf-qarshi'),
    (SELECT competition_id FROM competition WHERE slug = 'afc-champions-league'),
    (SELECT stage_id FROM stage WHERE name = 'ROUND OF 16' AND _competition_id = (SELECT competition_id FROM competition WHERE slug = 'afc-champions-league'))
);
INSERT INTO result (_event_id, home_goals, away_goals, winner) VALUES (LAST_INSERT_ID(), 1, 2, 'Nasaf');
 
-- AFC Match 2: Al Hilal vs Shabab Al Ahli (scheduled)
INSERT INTO event (season, status, date_venue, time_venue_utc, _home_team_id, _away_team_id, _competition_id, _stage_id) VALUES (
    2024, 'scheduled', '2024-01-03', '16:00:00',
    (SELECT team_id FROM team WHERE slug = 'al-hilal-saudi-fc'),
    (SELECT team_id FROM team WHERE slug = 'shabab-al-ahli-club'),
    (SELECT competition_id FROM competition WHERE slug = 'afc-champions-league'),
    (SELECT stage_id FROM stage WHERE name = 'ROUND OF 16' AND _competition_id = (SELECT competition_id FROM competition WHERE slug = 'afc-champions-league'))
);
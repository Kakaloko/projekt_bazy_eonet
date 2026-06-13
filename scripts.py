
schema = """

DROP TABLE IF EXISTS import_log;
DROP TABLE IF EXISTS event_category;
DROP TABLE IF EXISTS event_source;
DROP TABLE IF EXISTS event_geometry;
DROP TABLE IF EXISTS source;
DROP TABLE IF EXISTS category;
DROP TABLE IF EXISTS geometry;
DROP TABLE IF EXISTS geometry_type;
DROP TABLE IF EXISTS event_location;
DROP TABLE IF EXISTS event;

CREATE TABLE event (
	id INTEGER PRIMARY KEY, -- Przychodzi z API jako EONET_x zapisujemy tylko x
	title  VARCHAR(255) NOT NULL, -- Do przecinka z tego co przydchodzi w polu title
	description TEXT,
	start_date TIMESTAMP NOT NULL,
	end_date TIMESTAMP
);

CREATE TABLE event_location (
    id SERIAL PRIMARY KEY,
    event_id INTEGER NOT NULL, 
    country_code CHAR(2),
    country VARCHAR(100),
    state VARCHAR(100),
    city VARCHAR(100),

   
    CONSTRAINT fk_event_location_event
        FOREIGN KEY (event_id) 
        REFERENCES event(id)
		ON UPDATE CASCADE 
        ON DELETE CASCADE
);

CREATE TABLE geometry_type (
	id SERIAL PRIMARY KEY,
	type VARCHAR(100) NOT NULL
);

CREATE TABLE geometry (
	id SERIAL PRIMARY KEY, -- Własny z sql
	latitude FLOAT NOT NULL CHECK (90 >= latitude AND latitude >= -90), --latitude i longitude są w takich zakresach
	longitude FLOAT NOT NULL CHECK (180 >= longitude AND longitude >= -180),
	type_id INTEGER NOT NULL,
	magnitude FLOAT,
	unit VARCHAR(50),
	measure_date TIMESTAMP NOT NULL,

	CONSTRAINT fk_geometry_type_geometry
		FOREIGN KEY (type_id)
		REFERENCES geometry_type(id)
		ON UPDATE CASCADE
		ON DELETE RESTRICT --nie chcemy usunąć typu punktu który jest zapisany w bazie
);

CREATE TABLE category (
	id SERIAL PRIMARY KEY,
	abbreviation VARCHAR(50) NOT NULL,
	title VARCHAR(255) NOT NULL,
	description TEXT
);

CREATE TABLE source (
	id SERIAL PRIMARY KEY,
	abbreviation VARCHAR(50) NOT NULL,
	title VARCHAR(255) NOT NULL,
	description TEXT
	
);

CREATE TABLE event_category (
	event_id INTEGER NOT NULL,
	category_id INTEGER NOT NULL,

	CONSTRAINT pk_event_category
		PRIMARY KEY (event_id, category_id),
		
	CONSTRAINT fk_event_category_event
		FOREIGN KEY (event_id)
		REFERENCES event(id)
		ON UPDATE CASCADE
		ON DELETE CASCADE,

	CONSTRAINT fk_event_category_category
		FOREIGN KEY (category_id)
		REFERENCES category(id)
		ON UPDATE CASCADE
		ON DELETE CASCADE
);

CREATE TABLE event_source (
	event_id INTEGER  NOT NULL,
	source_id INTEGER NOT  NULL,

	
	CONSTRAINT pk_event_source
		PRIMARY KEY (event_id, source_id),

	CONSTRAINT fk_event_source_event
		FOREIGN KEY (event_id)
		REFERENCES event(id)
		ON UPDATE CASCADE
		ON DELETE CASCADE,

	CONSTRAINT fk_event_source_source
		FOREIGN KEY (source_id)
		REFERENCES source(id)
		ON UPDATE CASCADE
		ON DELETE CASCADE
);

CREATE TABLE event_geometry (
	event_id INTEGER NOT NULL,
	geometry_id INTEGER NOT NULL,


	CONSTRAINT pk_event_geometry
		PRIMARY KEY (event_id, geometry_id),

	CONSTRAINT fk_event_geometry_event
		FOREIGN KEY (event_id)
		REFERENCES event(id)
		ON UPDATE CASCADE
		ON DELETE CASCADE,

	CONSTRAINT fk_event_geometry
		FOREIGN KEY (geometry_id)
		REFERENCES geometry(id)
		ON UPDATE CASCADE
		ON DELETE CASCADE

);

CREATE TABLE import_log (
    id SERIAL PRIMARY KEY,
    imported_at TIMESTAMP NOT NULL,
    apiname VARCHAR(255) NOT NULL,
    endpoint VARCHAR(255) NOT NULL,
    records_received INTEGER NOT NULL,
    records_saved INTEGER NOT NULL,
    status VARCHAR(100) NOT NULL,
    error_message TEXT NOT NULL
);
"""


analyze_1 = """
SELECT 
    c.title AS category_name, 
    c.abbreviation AS abbreviation,
    COUNT(ec.event_id) AS amount_of_events
FROM category c
JOIN event_category ec ON c.id = ec.category_id
GROUP BY c.title, c.abbreviation
ORDER BY amount_of_events DESC
LIMIT 10;
"""

analyze_2 = """
SELECT 
    el.country AS country, 
    COUNT(e.id) AS amount_of_events
FROM event e
JOIN event_location el ON e.id = el.event_id
WHERE el.country IS NOT NULL
GROUP BY el.country
ORDER BY amount_of_events DESC
LIMIT 10;
"""


analyze_3 ="""

SELECT 
    e.title AS event_title,
    e.start_date AS start_date,
    s.title AS data_source
FROM event e
JOIN event_source es ON e.id = es.event_id
JOIN source s ON es.source_id = s.id
WHERE e.end_date IS NULL
ORDER BY e.start_date DESC
LIMIT 10;

"""


analyze_4 ="""
SELECT DISTINCT
    c.title AS category_name,
    e.title AS event_title,
    g.magnitude AS max_magnitude
FROM category c
JOIN event_category ec ON c.id = ec.category_id
JOIN event e ON ec.event_id = e.id
JOIN event_geometry eg ON e.id = eg.event_id
JOIN geometry g ON eg.geometry_id = g.id
WHERE e.id = (
    SELECT ec_sub.event_id
    FROM event_category ec_sub
    JOIN event_geometry eg_sub ON ec_sub.event_id = eg_sub.event_id
    JOIN geometry g_sub ON eg_sub.geometry_id = g_sub.id
    WHERE ec_sub.category_id = c.id
    ORDER BY g_sub.magnitude DESC NULLS LAST
    LIMIT 1
)
AND g.magnitude = (
    SELECT MAX(g_sub2.magnitude) 
    FROM event_geometry eg_sub2 
    JOIN geometry g_sub2 ON eg_sub2.geometry_id = g_sub2.id 
    WHERE eg_sub2.event_id = e.id
); 

"""


analyze_5 ="""

WITH MaksymalneCzasy AS (
    SELECT 
        c.id AS category_id,
        MAX(e.end_date - e.start_date) AS max_how_long
    FROM category AS c
    JOIN event_category AS ec ON ec.category_id = c.id
    JOIN event AS e ON e.id = ec.event_id
    WHERE e.end_date IS NOT NULL
    GROUP BY c.id
)
SELECT 
    c.title AS category_name,
    e.title AS event_name,
    (e.end_date - e.start_date) AS how_long
FROM category AS c
JOIN event_category AS ec ON ec.category_id = c.id
JOIN event AS e ON e.id = ec.event_id
JOIN MaksymalneCzasy mc 
    ON mc.category_id = c.id 
    AND (e.end_date - e.start_date) = mc.max_how_long;

"""
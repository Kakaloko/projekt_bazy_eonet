
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
	unit FLOAT,
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
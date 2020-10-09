BEGIN TRANSACTION;
PRAGMA encoding='UTF-8'

CREATE TABLE config (
    id  INTEGER PRIMARY KEY,
    key VARCHAR(512) UNIQUE NOT NULL,
    value VARCHAR(1024) DEFAULT ''
);

CREATE TABLE breeder (
    id INTEGER PRIMARY KEY,
    name VARCHAR(256) UNIQUE NOT NULL,
    homepage VARCHAR(1024)
);

CREATE TABLE strain (
    id INTEGER PRIMARY KEY,
    breeder INTEGER NOT NULL,
    name VARCHAR(256),
    info VARCHAR(1048576),
    description VARCHAR(1048576),
    homepage VARCHAR(1024),
    seedfinder VARCHAR(1024),
    FOREIGN KEY (breeder) REFERENCES breeder(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    UNIQUE (name,breeder)
);

CREATE VIEW strain_view AS
    SELECT  t1.id AS id,
            t1.breeder AS breeder_id,
            t2.name AS breeder_name,
            t2.homepage AS breeder_homepage,
            t1.name AS name,
            t1.info AS info,
            t1.description AS description,
            t1.homepage AS homepage,
            t1.seedfinder AS seedfinder
        FROM strain AS t1 JOIN breeder AS t2
            ON t1.breeder = t2.id;
            
CREATE TABLE growlog (
    id INTEGER PRIMARY KEY,
    title VARCHAR(1024) UNIQUE NOT NULL,
    description VARCHAR(1048576),
    created_on TIMESTAMP NOT NULL,
    flower_on DATE DEFAULT '',
    finished_on TIMESTAMP DEFAULT '',
    UNIQUE(title)
);

CREATE TABLE growlog_entry (
    id INTEGER PRIMARY KEY,
    growlog INTEGER NOT NULL,
    created_on TIMESTAMP NOT NULL,
    entry VARCHAR(1048576),
    FOREIGN KEY (growlog) REFERENCES growlog(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE TABLE growlog_strain (
    id INTEGER PRIMARY KEY,
    growlog INTEGER NOT NULL,
    strain INTEGER NOT NULL,
    UNIQUE (growlog,strain),
    FOREIGN KEY (growlog) REFERENCES growlog(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    FOREIGN KEY (strain) REFERENCES strain(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

COMMIT;

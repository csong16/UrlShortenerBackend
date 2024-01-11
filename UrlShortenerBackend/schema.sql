DROP TABLE IF EXISTS url_mapping;

CREATE TABLE url_mapping (
    url_id TEXT PRIMARY KEY,
    mapped_url TEXT NOT NULL
);
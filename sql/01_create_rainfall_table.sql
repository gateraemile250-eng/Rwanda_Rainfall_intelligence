CREATE TABLE rainfall_observations (
    date DATE NOT NULL,
    adm_level INTEGER NOT NULL,
    adm_id INTEGER NOT NULL,
    pcode VARCHAR(10) NOT NULL,
    n_pixels INTEGER NOT NULL,

    rfh DOUBLE PRECISION,
    rfh_avg DOUBLE PRECISION,
    r1h DOUBLE PRECISION,
    r1h_avg DOUBLE PRECISION,
    r3h DOUBLE PRECISION,
    r3h_avg DOUBLE PRECISION,
    rfq DOUBLE PRECISION,
    r1q DOUBLE PRECISION,
    r3q DOUBLE PRECISION,

    version VARCHAR(20) NOT NULL,

    PRIMARY KEY (date, adm_id, version)
);
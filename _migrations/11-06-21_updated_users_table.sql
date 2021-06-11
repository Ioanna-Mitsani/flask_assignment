CREATE TABLE user (
    username    VARCHAR     NOT NULL
                            COLLATE RTRIM,
    email       VARCHAR     NOT NULL,
    password    VARCHAR     NOT NULL
                            COLLATE RTRIM,
    f_name      VARCHAR     NOT NULL,
    l_name      VARCHAR     NOT NULL,
    uid         INTEGER     PRIMARY KEY AUTOINCREMENT
                            NOT NULL,
    address     TEXT        COLLATE NOCASE,
    city        TEXT        COLLATE NOCASE,
    country     TEXT        COLLATE NOCASE,
    postal_code INTEGER (5),
    about       TEXT        COLLATE NOCASE
);

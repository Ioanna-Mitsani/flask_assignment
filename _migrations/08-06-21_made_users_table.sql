CREATE TABLE user (
    username VARCHAR NOT NULL,
    email    VARCHAR PRIMARY KEY
                     NOT NULL,
    pwd      VARCHAR NOT NULL,
    f_name   VARCHAR NOT NULL,
    l_name   VARCHAR NOT NULL,
    dob      DATE
);

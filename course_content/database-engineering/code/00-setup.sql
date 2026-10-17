-- Practice database used in every session. Run it once:  psql -d course -f 00-setup.sql
SET client_min_messages = warning;
DROP TABLE IF EXISTS movie_cast, movies, actors, directors CASCADE;

CREATE TABLE directors (
    director_id SERIAL PRIMARY KEY,
    name        VARCHAR(60) NOT NULL
);

CREATE TABLE movies (
    movie_id    SERIAL PRIMARY KEY,
    title       VARCHAR(80) NOT NULL,
    year        INT NOT NULL CHECK (year > 1900),
    genre       VARCHAR(30),
    rating      NUMERIC(3,1),             -- made-up practice scores, not real reviews
    director_id INT REFERENCES directors(director_id)
);

CREATE TABLE actors (
    actor_id SERIAL PRIMARY KEY,
    name     VARCHAR(60) NOT NULL
);

CREATE TABLE movie_cast (
    movie_id INT REFERENCES movies(movie_id),
    actor_id INT REFERENCES actors(actor_id),
    PRIMARY KEY (movie_id, actor_id)
);

INSERT INTO directors (name) VALUES
 ('Mani Ratnam'), ('Suresh Krissna'), ('K. S. Ravikumar'), ('Shankar'),
 ('Mari Selvaraj'), ('Lokesh Kanagaraj'), ('Sudha Kongara'), ('Vetrimaaran');

INSERT INTO movies (title, year, genre, rating, director_id) VALUES
 ('Nayakan',             1987, 'Crime',  9.0, 1),
 ('Thalapathi',          1991, 'Drama',  8.5, 1),
 ('Baasha',              1995, 'Action', 8.2, 2),
 ('Muthu',               1995, 'Comedy', 7.5, 3),
 ('Sivaji',              2007, 'Action', 7.8, 4),
 ('Pariyerum Perumal',   2018, 'Drama',  8.7, 5),
 ('Kaithi',              2019, 'Action', 8.4, 6),
 ('Soorarai Pottru',     2020, 'Drama',  8.6, 7),
 ('Karnan',              2021, 'Drama',  8.0, 5),
 ('Vikram',              2022, 'Action', 8.3, 6),
 ('Untitled Project',    2026, NULL,     NULL, NULL);

INSERT INTO actors (name) VALUES
 ('Kamal Haasan'), ('Rajinikanth'), ('Mammootty'), ('Dhanush'), ('Suriya'),
 ('Fahadh Faasil'), ('Vijay Sethupathi'), ('Karthi'), ('Kathir');

INSERT INTO movie_cast (movie_id, actor_id) VALUES
 (1,1), (2,2), (2,3), (3,2), (4,2), (5,2), (6,9), (7,8),
 (8,5), (9,4), (10,1), (10,5), (10,6), (10,7);

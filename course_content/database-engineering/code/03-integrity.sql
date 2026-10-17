\echo '-- entity integrity: a duplicate primary key is refused'
INSERT INTO movies (movie_id, title, year) VALUES (1, 'Duplicate', 2000);
\echo '-- referential integrity: director 99 does not exist'
INSERT INTO movies (title, year, director_id) VALUES ('Ghost Film', 2000, 99);
\echo '-- domain integrity: year must be a number above 1900'
INSERT INTO movies (title, year) VALUES ('Too Old', 1800);
\echo '-- NOT NULL: a title is required'
INSERT INTO movies (year) VALUES (2000);
\echo '-- deleting a director who still has movies is refused'
DELETE FROM directors WHERE name = 'Mani Ratnam';
\echo '-- a valid row works'
INSERT INTO movies (title, year, genre, director_id) VALUES ('Test Film', 2024, 'Drama', 1) RETURNING movie_id, title;
DELETE FROM movies WHERE title = 'Test Film';

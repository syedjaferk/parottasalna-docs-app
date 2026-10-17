\echo '-- one column'
SELECT title FROM movies;
\echo '-- several columns, with aliases'
SELECT title AS film, year AS released FROM movies;
\echo '-- computed column'
SELECT title, year, 2026 - year AS age_in_years FROM movies;
\echo '-- ORDER BY, newest first, then title'
SELECT title, year FROM movies ORDER BY year DESC, title ASC;
\echo '-- DISTINCT removes repeats'
SELECT DISTINCT genre FROM movies ORDER BY genre;
\echo '-- DISTINCT on two columns'
SELECT DISTINCT genre, year FROM movies WHERE year = 1995 ORDER BY genre;

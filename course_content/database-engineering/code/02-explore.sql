\echo '-- tables in the database'
\dt
\echo '-- shape of one table'
\d movies
\echo '-- how many rows in each table'
SELECT 'directors' AS table_name, count(*) FROM directors
UNION ALL SELECT 'movies', count(*) FROM movies
UNION ALL SELECT 'actors', count(*) FROM actors
UNION ALL SELECT 'movie_cast', count(*) FROM movie_cast;

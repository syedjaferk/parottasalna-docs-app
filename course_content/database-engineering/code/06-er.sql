\echo '-- one-to-many: one director, many movies (movies.director_id points at directors)'
\d movies
\echo '-- many-to-many: movie_cast holds one row per (movie, actor) pair'
\d movie_cast
\echo '-- the same actor in many movies, and a movie with many actors'
SELECT actor_id, count(*) AS movies_acted FROM movie_cast GROUP BY actor_id ORDER BY movies_acted DESC, actor_id LIMIT 3;
SELECT movie_id, count(*) AS cast_size FROM movie_cast GROUP BY movie_id ORDER BY cast_size DESC LIMIT 1;

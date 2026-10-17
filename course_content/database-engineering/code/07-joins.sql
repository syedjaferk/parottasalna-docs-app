\echo '-- INNER JOIN: only movies that have a director'
SELECT m.title, d.name AS director FROM movies m INNER JOIN directors d ON d.director_id = m.director_id ORDER BY m.year;
\echo '-- LEFT JOIN: keep every movie, even without a director'
SELECT m.title, d.name AS director FROM movies m LEFT JOIN directors d ON d.director_id = m.director_id ORDER BY m.year DESC LIMIT 3;
\echo '-- LEFT JOIN from directors: who has no movies?'
SELECT d.name FROM directors d LEFT JOIN movies m ON m.director_id = d.director_id WHERE m.movie_id IS NULL;
\echo '-- joining three tables: movie, actor, via the link table'
SELECT m.title, a.name AS actor FROM movies m JOIN movie_cast mc ON mc.movie_id = m.movie_id JOIN actors a ON a.actor_id = mc.actor_id WHERE m.title = 'Vikram' ORDER BY a.name;
\echo '-- join plus GROUP BY: movies per director'
SELECT d.name, count(m.movie_id) AS movies FROM directors d LEFT JOIN movies m ON m.director_id = d.director_id GROUP BY d.name ORDER BY movies DESC, d.name;
\echo '-- the classic mistake: forgetting ON gives every combination'
SELECT count(*) AS rows_without_on FROM movies, directors;
SELECT count(*) AS rows_with_on FROM movies m JOIN directors d ON d.director_id = m.director_id;

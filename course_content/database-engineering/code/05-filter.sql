\echo '-- WHERE'
SELECT title, year FROM movies WHERE genre = 'Action';
\echo '-- AND'
SELECT title, year FROM movies WHERE genre = 'Action' AND year > 2000;
\echo '-- OR'
SELECT title, genre FROM movies WHERE genre = 'Crime' OR genre = 'Comedy';
\echo '-- IN'
SELECT title, year FROM movies WHERE year IN (1995, 2021);
\echo '-- BETWEEN is inclusive'
SELECT title, rating FROM movies WHERE rating BETWEEN 8.0 AND 8.5 ORDER BY rating;
\echo '-- LIKE and ILIKE'
SELECT title FROM movies WHERE title LIKE 'S%';
SELECT title FROM movies WHERE title ILIKE '%pottru';
\echo '-- = NULL never matches. IS NULL does'
SELECT title FROM movies WHERE genre = NULL;
SELECT title FROM movies WHERE genre IS NULL;
\echo '-- LIMIT and OFFSET, FETCH'
SELECT title, rating FROM movies WHERE rating IS NOT NULL ORDER BY rating DESC LIMIT 3;
SELECT title, rating FROM movies WHERE rating IS NOT NULL ORDER BY rating DESC OFFSET 3 FETCH FIRST 2 ROWS ONLY;
\echo '-- AND binds tighter than OR: parentheses change the answer'
SELECT title, genre, year FROM movies WHERE genre = 'Drama' OR genre = 'Action' AND year > 2015 ORDER BY year;
SELECT title, genre, year FROM movies WHERE (genre = 'Drama' OR genre = 'Action') AND year > 2015 ORDER BY year;

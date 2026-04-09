-- Apply transformations to produce a summary table with the following fields:
-- publication year,
-- book_count published that year,
-- average_price of books published that year in USD rounded to cents using convertion rate €1 = $1.2.

CREATE TABLE books_summary AS
SELECT 
	year AS publication_year, 
	COUNT(*) AS book_count, 
	ROUND(AVG(price_in_dollars), 2) AS average_price
FROM books
GROUP BY year;

SELECT * FROM books_summary;

SELECT * FROM books;
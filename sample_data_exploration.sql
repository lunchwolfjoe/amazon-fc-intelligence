-- Sample data exploration (replace table_name with actual table)
SELECT *
FROM information_schema.columns
WHERE table_name = 'your_table_name'
ORDER BY ordinal_position;
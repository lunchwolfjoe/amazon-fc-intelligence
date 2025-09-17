-- Get row counts for major tables (replace with actual table names)
SELECT 'employees' as table_name, COUNT(*) as row_count FROM employees
UNION ALL
SELECT 'compensation' as table_name, COUNT(*) as row_count FROM compensation
UNION ALL  
SELECT 'job_levels' as table_name, COUNT(*) as row_count FROM job_levels;
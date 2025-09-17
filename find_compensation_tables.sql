-- Find tables related to compensation
SELECT table_schema,
       table_name,
       table_type
FROM information_schema.tables 
WHERE (table_name ILIKE '%comp%' 
       OR table_name ILIKE '%salary%' 
       OR table_name ILIKE '%wage%'
       OR table_name ILIKE '%pay%'
       OR table_name ILIKE '%employee%'
       OR table_name ILIKE '%job%')
ORDER BY table_schema, table_name;
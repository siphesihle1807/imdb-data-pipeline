SELECT 'title_basics' as table_name, COUNT(*) as rows FROM demo_dataset.title_basics
UNION ALL
SELECT 'title_ratings', COUNT(*) FROM demo_dataset.title_ratings
UNION ALL
SELECT 'name_basics', COUNT(*) FROM demo_dataset.name_basics;
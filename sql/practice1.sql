SELECT DISTINCT "City"
FROM public.salary_data2
ORDER BY "City";

CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    score INTEGER
);


INSERT INTO students (name, score) VALUES ('小明', 95);
SELECT * FROM students;

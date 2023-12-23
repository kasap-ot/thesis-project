CREATE OR REPLACE FUNCTION applicants (offer_id_v INT)
RETURNS TABLE (
    id INT,
    email VARCHAR(255),
    name VARCHAR(255),
    date_of_birth DATE,
    university VARCHAR(255),
    major VARCHAR(255),
    credits INT,
    gpa FLOAT,
    status status
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT s.id, s.email, s.name, s.date_of_birth, s.university, s.major, s.credits, s.gpa, a.status
    FROM students s
    JOIN applications a ON s.id = a.student_id
    WHERE a.offer_id = offer_id_v;
END;
$$;


CREATE OR REPLACE FUNCTION my_applications(p_student_id INT)
RETURNS TABLE (
    field VARCHAR(255),
    salary INT,
    num_weeks INT,
    status status,
    student_id INT,
    offer_id INT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT o.field, o.salary, o.num_weeks, a.status, a.student_id, a.offer_id
    FROM offers o
    JOIN applications a ON o.id = a.offer_id
    WHERE a.student_id = p_student_id;
END;
$$;

DROP FUNCTION my_applications(p_student_id INT);
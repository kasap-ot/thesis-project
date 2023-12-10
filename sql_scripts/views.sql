CREATE OR REPLACE FUNCTION applicants (offer_id_v INT)
RETURNS TABLE (
    id INT,
    email VARCHAR(255),
    name VARCHAR(255),
    date_of_birth DATE,
    university VARCHAR(255),
    major VARCHAR(255),
    credits INT,
    gpa FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT s.id, s.email, s.name, s.date_of_birth, s.university, s.major, s.credits, s.gpa
    FROM students s
    JOIN applications a ON s.id = a.student_id
    WHERE a.offer_id = offer_id_v;
END;
$$;

CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    age INT NOT NULL,
    university VARCHAR(255) NOT NULL,
    major VARCHAR(255) NOT NULL,
    credits INT NOT NULL,
    gpa FLOAT NOT NULL
);


CREATE TABLE IF NOT EXISTS companies (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    field VARCHAR(255) NOT NULL,
    num_employees VARCHAR(255) NOT NULL,
    year_founded INT NOT NULL,
    website VARCHAR(255) NOT NULL
);


CREATE TABLE IF NOT EXISTS offers (
    id SERIAL PRIMARY KEY,
    salary INT NOT NULL,
    num_weeks INT NOT NULL,
    field VARCHAR(255) NOT NULL,
    deadline DATE NOT NULL,
    requirements TEXT NOT NULL,
    responsibilities TEXT NOT NULL
);


CREATE TABLE IF NOT EXISTS experiences (
    id SERIAL PRIMARY KEY,
    from_date DATE NOT NULL,
    to_date DATE NOT NULL,
    company VARCHAR(255) NOT NULL,
    position VARCHAR(255) NOT NULL,
    description TEXT NOT NULL
);


CREATE DOMAIN status INT CHECK (VALUE >= 0 AND VALUE <= 2);


CREATE TABLE IF NOT EXISTS applications (
    student_id INT REFERENCES students(id),
    offer_id INT REFERENCES offers(id),
    status status NOT NULL,
    PRIMARY KEY (student_id, offer_id)
);


-- Add table for regions

CREATE TABLE IF NOT EXISTS regions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);


-- Add table for subjects

CREATE TABLE IF NOT EXISTS subjects (
    student_id INT REFERENCES students(id),
    name VARCHAR(255),
    grade INT NOT NULL CHECK (grade BETWEEN 5 AND 10),
    PRIMARY KEY (student_id, name)
);


-- Add table for motivational letter
-- (made as separate table for easier extensibility)

CREATE TABLE IF NOT EXISTS motivational_letters (
    student_id INT PRIMARY KEY REFERENCES students(id),
    about_me_section TEXT NOT NULL,
    skills_section TEXT NOT NULL,
    looking_for_section TEXT NOT NULL
);


-- Add table for student reports by companies

CREATE TABLE IF NOT EXISTS student_reports (
    student_id INT REFERENCES students(id),
    offer_id INT REFERENCES offers(id),
    overall_grade INT NOT NULL CHECK (overall_grade BETWEEN 1 AND 10),
    technical_grade INT NOT NULL CHECK (overall_grade BETWEEN 1 AND 10),
    communication_grade INT NOT NULL CHECK (overall_grade BETWEEN 1 AND 10),
    comment TEXT NOT NULL,
    PRIMARY KEY (student_id, offer_id)
)


-- Add table for company reports

CREATE DOMAIN report_grade INT CHECK (VALUE BETWEEN 1 AND 10);

CREATE TABLE IF NOT EXISTS company_reports (
    student_id INT REFERENCES students(id),
    offer_id INT REFERENCES offers(id),
    mentorship_grade report_grade NOT NULL,
    work_environment_grade report_grade NOT NULL,
    benefits_grade report_grade NOT NULL,
    comment TEXT NOT NULL,
    PRIMARY KEY (student_id, offer_id)
)
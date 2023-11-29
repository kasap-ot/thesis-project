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
    -- company_id [FOREIGN KEY]
);


CREATE TABLE IF NOT EXISTS experiences (
    id SERIAL PRIMARY KEY,
    from_date DATE NOT NULL,
    to_date DATE NOT NULL,
    company VARCHAR(255) NOT NULL,
    description TEXT NOT NULL
    -- student_id [FOREIGN KEY]
);


-- CREATE TABLE IF NOT EXISTS applications (
--     student_id,
--     offer_id,
--     status
-- );
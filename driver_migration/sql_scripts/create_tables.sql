CREATE TABLE IF NOT EXISTS students (
    id INT SERIAL KEY,
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
    id INT SERIAL KEY,
    email VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    field VARCHAR(255) NOT NULL,
    num_employees VARCHAR(255) NOT NULL,
    year_founded INT NOT NULL,
    website VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS offers (
    id INT SERIAL KEY,
    salary INT NOT NULL,
    num_weeks INT NOT NULL,
    field INT NOT NULL,
    deadline DATE NOT NULL,
    requirements TEXT NOT NULL,
    responsibilities TEXT NOT NULL
);


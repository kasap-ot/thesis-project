-- Add offer-company and experience-student relationships

ALTER TABLE offers ADD COLUMN
company_id INT NOT NULL REFERENCES companies(id)
ON DELETE SET NULL
ON UPDATE CASCADE;


ALTER TABLE experiences ADD COLUMN
student_id INT NOT NULL REFERENCES students(id)
ON DELETE SET NULL
ON UPDATE CASCADE;


-- Modify offer-company relationship

ALTER TABLE offers
DROP CONSTRAINT IF EXISTS offers_company_id_fkey;

ALTER TABLE offers
ADD CONSTRAINT offers_company_id_fkey
FOREIGN KEY (company_id)
REFERENCES companies(id)
ON DELETE SET DEFAULT
ON UPDATE CASCADE;

ALTER TABLE offers
ALTER COLUMN company_id SET DEFAULT -1;


-- Add user email uniqueness constraints

ALTER TABLE students
ADD CONSTRAINT students_unique_email_constraint UNIQUE (email);

ALTER TABLE companies
ADD CONSTRAINT companies_unique_email_constraint UNIQUE (email);


-- Change "age" to "date_of_birth" for studends

ALTER TABLE students
DROP COLUMN age;

ALTER TABLE students
ADD COLUMN date_of_birth DATE NOT NULL DEFAULT '2020-01-01';

ALTER TABLE students
ALTER COLUMN date_of_birth DROP DEFAULT;


-- Add relationships for student-region and offer-region

ALTER TABLE students
ADD COLUMN region_id INT NOT NULL REFERENCES region(id)
ON DELETE SET DEFAULT
ON UPDATE CASCADE;

ALTER TABLE students
ALTER COLUMN region_id SET DEFAULT -1;

ALTER TABLE offers
ADD COLUMN region_id INT NOT NULL REFERENCES region(id)
ON DELETE SET DEFAULT
ON UPDATE CASCADE;

ALTER TABLE offers
ALTER COLUMN region_id SET DEFAULT -1;


-- Drop NOT NULL constraint on company_id for offers

ALTER TABLE offers ALTER COLUMN company_id DROP NOT NULL;


-- Modify status domain to have text fields instead of integers

ALTER TABLE applications
DROP COLUMN status

DROP PROCEDURE accept_student;
DROP PROCEDURE cancel_application;
DROP FUNCTION applicants;

DROP DOMAIN status;

CREATE DOMAIN status TEXT 
CHECK (VALUE IN ('WAITING', 'ACCEPTED', 'REJECTED'));

ALTER TABLE applications
ADD COLUMN status status NOT NULL;

-- Don't forget to recreate the 
-- dropped procedures and functions


-- Add values to the status-domain - ONGOING and COMPLETED

ALTER DOMAIN status DROP CONSTRAINT status_check;
ALTER DOMAIN status ADD CONSTRAINT status_check
CHECK (VALUE IN (
    'WAITING', 
    'ACCEPTED', 
    'REJECTED', 
    'ONGOING', 
    'COMPLETED'
));


--  Add profile picture path column for students and companies

ALTER TABLE students 
ADD COLUMN profile_picture_path VARCHAR(255) DEFAULT NULL;

ALTER TABLE companies
ADD COLUMN profile_picture_path VARCHAR(255) DEFAULT NULL;


-- Add description to companies

ALTER TABLE companies
ADD COLUMN description TEXT DEFAULT NULL;
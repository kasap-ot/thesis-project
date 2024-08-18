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
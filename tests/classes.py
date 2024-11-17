from dataclasses import dataclass


@dataclass
class CompanyTest:
    id: int
    email: str
    password: str
    hashed_password: str
    name: str
    field: str
    num_employees: int
    year_founded: int
    website: str
    description: str


@dataclass
class OfferTest:
    id: int
    salary: int
    num_weeks: int
    field: str
    deadline: str
    requirements: str
    responsibilities: str
    company_id: int
    region_id: int


@dataclass
class StudentTest:
    id: int
    email: str
    name: str
    date_of_birth: str
    university: str
    major: str
    credits: int
    gpa: float
    region_id: int
    password: str
    hashed_password: str


@dataclass
class ExperienceTest:
    id: int
    from_date: str
    to_date: str
    company: str
    position: str
    description: str
    student_id: int


@dataclass
class ApplicationTest:
    student_id: int
    offer_id: int
    status: str


@dataclass
class SubjectTest:
    student_id: int
    name: str
    grade: int


@dataclass 
class MotivationalLetterTest:
    student_id: int
    about_me_section: str
    skills_section: str
    looking_for_section: str


@dataclass
class StudentReportTest:
    student_id: int
    offer_id: int
    overall_grade: int
    technical_grade: int
    communication_grade: int
    comment: str


@dataclass
class CompanyReportTest:
    student_id: int
    offer_id: int
    mentorship_grade: int
    work_environment_grade: int
    benefits_grade: int
    comment: str


@dataclass
class RegionTest:
    id: int
    name: str
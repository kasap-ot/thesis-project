from typing import LiteralString, Optional
from .enums import Status, UserType


# SQL query functions


def accept_student_query() -> LiteralString:
    return (
        f"UPDATE applications SET status = '{Status.ACCEPTED.value}' "
        f"WHERE student_id = %s AND offer_id = %s AND status = '{Status.WAITING.value}' "
        "RETURNING student_id;"
    )


def reject_students_query() -> LiteralString:
    return (
        f"UPDATE applications SET status = '{Status.REJECTED.value}' "
        f"WHERE student_id <> %s AND offer_id = %s AND status = '{Status.WAITING.value}' "
        "RETURNING student_id;"
    )


def select_applications_query() -> LiteralString:
    return (
        "SELECT "
            "o.field, o.salary, o.num_weeks, "
            "a.status, a.student_id, a.offer_id "
        "FROM offers o "
        "JOIN applications a ON o.id = a.offer_id "
        "WHERE a.student_id = %s;"
    )


def insert_student_query() -> LiteralString:
    return (
        "INSERT INTO students "
        "(email, hashed_password, name, date_of_birth, university, major, credits, gpa, region_id) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    )


def update_student_query() -> LiteralString:
    return (
        "UPDATE students SET "
        "email=%s, name=%s, date_of_birth=%s, university=%s, "
        "major=%s, credits=%s, gpa=%s WHERE id=%s "
        "RETURNING *;"
    )


def insert_company_query() -> LiteralString:
    return (
        "INSERT INTO companies "
        "(email, hashed_password, name, field, num_employees, year_founded, website) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s)"
    )


def select_company_offers_query() -> LiteralString:
    return (
        "SELECT o.id, o.salary, o.num_weeks, o.field, o.deadline, o.requirements, o.responsibilities, o.company_id, r.name as region "
        "FROM offers as o "
        "JOIN regions as r ON o.region_id = r.id "
        "WHERE o.company_id = %s;"
    )


def update_company_query() -> LiteralString:
    return (
        "UPDATE companies SET "
        "email=%s, name=%s, field=%s, num_employees=%s, year_founded=%s, website=%s "
        "WHERE id=%s RETURNING *;"
    )


def insert_offer_query() -> LiteralString:
    return (
        "INSERT INTO offers "
        "(salary, num_weeks, field, deadline, requirements, responsibilities, company_id, region_id) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    )


def select_offers_query(field: str | None) -> LiteralString:
    query = (
        "SELECT o.id, o.salary, o.num_weeks, o.field, o.deadline, r.name as region, c.name AS company_name "
        "FROM offers AS o "
        "JOIN companies AS c ON o.company_id = c.id "
        "JOIN regions AS r ON o.region_id = r.id "
        "WHERE o.num_weeks >= %s AND o.num_weeks <= %s "
        "AND o.salary >= %s AND o.salary <= %s "
        "AND (r.id = %s OR r.name = 'Global')"
    )
    if field is not None:
        query += " AND o.field = %s"
    return query


def select_offer_query() -> LiteralString:
    return (
        "SELECT o.id, o.salary, o.num_weeks, o.field, o.deadline, o.requirements, o.responsibilities, o.company_id, r.name as region "
        "FROM offers as o "
        "JOIN regions as r ON o.region_id = r.id "
        "WHERE o.id = %s;"
    )


def update_offer_query() -> LiteralString:
    return (
        "UPDATE offers SET "
        "salary=%s, num_weeks=%s, field=%s, deadline=%s, requirements=%s, responsibilities=%s "
        "WHERE id=%s "
        "RETURNING *;"
    )


def insert_experience_query() -> LiteralString:
    return (
        "INSERT INTO experiences "
        "(from_date, to_date, company, position, description, student_id) "
        "VALUES (%s, %s, %s, %s, %s, %s)"
    )


def update_experience_query() -> LiteralString:
    return (
        "UPDATE experiences SET "
        "from_date=%s, to_date=%s, company=%s, position=%s, description=%s "
        "WHERE id=%s "
        "RETURNING *;" # ? Do we need this query to return anything?
    )


def delete_application_query() -> LiteralString:
    return (
        "DELETE FROM applications "
        "WHERE student_id = %s AND offer_id = %s;"
    )


def update_applications_waiting_query() -> LiteralString:
    return (
        f"UPDATE applications SET status = '{Status.WAITING.value}' "
        "WHERE student_id <> %s AND offer_id = %s "
        "RETURNING student_id;"
    )


def select_applicants_query(
    offer_id: int, 
    university: Optional[str],
    min_gpa: float,
    max_gpa: float,
    min_credits: int,
    max_credits: int,
    subjects: list[tuple[str, int]],
) -> tuple[LiteralString, list]:
    query = (
        "SELECT "
            "s.id, s.email, s.name, s.date_of_birth, "
            "s.university, s.major, s.credits, s.gpa, "
            "s.region_id, a.status "
        "FROM students s "
        "JOIN applications a ON s.id = a.student_id "
        "WHERE a.offer_id = %s "
        "AND s.gpa >= %s AND s.gpa <= %s "
        "AND s.credits >= %s AND s.credits <= %s "
    )
    params = [offer_id, min_gpa,  max_gpa,  min_credits,  max_credits]
    
    if university is not None:
        query += " AND s.university LIKE %s"
        params.append(f"%{university}%")
    
    if not subjects:
        return query, params
        
    subjects_query, params = select_student_ids_by_subjects_query(subjects, params)
    query += f" AND s.id IN ({subjects_query})"
    
    return query, params


def select_student_ids_by_subjects_query(subjects: list[tuple], params: list) -> tuple[LiteralString, list]:
    query = (
        "SELECT DISTINCT(student_id) "
        "FROM subjects "
        "GROUP BY student_id HAVING "
    )
    for index, subject in enumerate(subjects):
        query += "COUNT(DISTINCT CASE WHEN name = %s AND grade >= %s THEN 1 END) > 0"
        if index != len(subjects) - 1:
            query += " AND "

        params.extend(subject)

    return query, params


def insert_subject_query() -> LiteralString:
    return "INSERT INTO subjects (student_id, name, grade) VALUES (%s, %s, %s);"


def select_offer_company_id_query() -> LiteralString:
    return "SELECT company_id FROM offers WHERE id = %s"


def delete_student_query() -> LiteralString:
    return "DELETE FROM students WHERE id = %s"


def select_student_with_motivational_letter_query() -> LiteralString:
    return (
        "SELECT * "
        "FROM students s "
        "LEFT JOIN motivational_letters ml "
        "ON s.id = ml.student_id " 
        "WHERE s.id = %s;"
    )


def select_student_experiences_query() -> LiteralString:
    return "SELECT * FROM experiences WHERE student_id = %s;"


def select_student_subjects_query() -> LiteralString:
    return "SELECT * FROM subjects WHERE student_id = %s;"


def select_company_query() -> LiteralString:
    return "SELECT * FROM companies WHERE id = %s;"


def delete_company_query() -> LiteralString:
    return "DELETE FROM companies WHERE id = %s"


def update_offer_company_id_null_query() -> LiteralString:
    return "UPDATE offers SET company_id = NULL WHERE id = %s"


def select_experience_student_id_query() -> LiteralString:
    return "SELECT student_id FROM experiences WHERE id = %s"


def delete_experience_query() -> LiteralString:
    return "DELETE FROM experiences WHERE id = %s"


def insert_application_query() -> LiteralString:
    return "INSERT INTO applications (student_id, offer_id, status) VALUES (%s, %s, %s)"


def select_application_status_query() -> LiteralString:
    return "SELECT status FROM applications WHERE student_id=%s AND offer_id=%s;"


def select_application_email_and_field_query() -> LiteralString:
    return (
        "SELECT students.email, offers.field "
        "FROM applications "
        "JOIN offers ON applications.offer_id = offers.id "
        "JOIN students ON applications.student_id = students.id "
        "WHERE applications.student_id = %s AND applications.offer_id = %s"
    )


def select_applications_emails_and_fields_query() -> LiteralString:
    return (
        "SELECT students.email, offers.field "
        "FROM applications "
        "JOIN offers ON applications.offer_id = offers.id "
        "JOIN students ON applications.student_id = students.id "
        "WHERE applications.student_id = ANY(%s) AND applications.offer_id = %s"
    )


def select_offer_email_and_field_query() -> LiteralString:
    return (
        "SELECT companies.email, offers.field "
        "FROM offers "
        "JOIN companies "
        "ON companies.id = offers.company_id "
        "WHERE offers.id = %s"
    )


def select_subject_student_id_query() -> LiteralString:
    return "SELECT student_id FROM subjects WHERE student_id = %s and name = %s;"


def update_subject_query() -> LiteralString:
    return (
        "UPDATE subjects "
        "SET grade = %s "
        "WHERE student_id = %s and name = %s;"
    )


def delete_subject_query() -> LiteralString:
    return "DELETE FROM subjects WHERE student_id = %s AND name = %s"


def insert_motivational_letter_query() -> LiteralString:
    return (
        "INSERT INTO motivational_letters "
        "(student_id, about_me_section, skills_section, looking_for_section) "
        "VALUES (%s, %s, %s, %s);"
    )


def select_motivational_letter_student_id_query() -> LiteralString:
    return "SELECT student_id FROM motivational_letters WHERE student_id = %s;"


def update_motivational_letter_query() -> LiteralString:
    return (
        "UPDATE motivational_letters SET "
        "about_me_section = %s, "
        "skills_section = %s, "
        "looking_for_section = %s;"
    )


def delete_motivational_letter_query() -> LiteralString:
    return "DELETE FROM motivational_letters WHERE student_id = %s;"


def insert_student_report_query() -> LiteralString:
    return (
        "INSERT INTO student_reports "
        "(overall_grade, technical_grade, communication_grade, comment, student_id, offer_id) "
        "VALUES (%s, %s, %s, %s, %s, %s);"
    )


def update_student_report_query() -> LiteralString:
    return (
        "UPDATE student_reports SET "
        "overall_grade = %s, "
        "technical_grade = %s, "
        "communication_grade = %s, "
        "comment = %s "
        "WHERE student_id = %s AND offer_id = %s"
    )


def delete_student_report_query() -> LiteralString:
    return "DELETE FROM student_reports WHERE student_id = %s AND offer_id = %s;"


def update_application_status_query(new_status: Status) -> LiteralString:
    return (
        f"UPDATE applications SET status = '{new_status.value}' "
        "WHERE student_id = %s AND offer_id = %s;"
    )


def select_student_report_query() -> LiteralString:
    return (
        "SELECT * "
        "FROM student_reports "
        "WHERE student_id = %s AND offer_id = %s;"
    )


def select_student_reports_query() -> LiteralString:
    return (
        "SELECT sr.overall_grade, sr.technical_grade, sr.communication_grade, sr.comment, "
        "o.num_weeks, o.field, c.name as company_name "
        "FROM student_reports sr "
        "JOIN offers o ON sr.offer_id = o.id "
        "JOIN companies c ON o.company_id = c.id "
        "WHERE sr.student_id = %s;"
    )


def select_company_reports_query() -> LiteralString:
    return (
        "SELECT "
            "cr.comment, cr.mentorship_grade, "
            "cr.work_environment_grade, cr.benefits_grade, "
            "o.field, o.num_weeks, s.name as student_name "
        "FROM company_reports cr "
        "JOIN students s  ON cr.student_id = s.id "
        "JOIN offers o    ON cr.offer_id = o.id "
        "JOIN companies c ON o.company_id = c.id "
        "WHERE c.id = %s;"
    )


def update_company_report_query() -> LiteralString:
    return (
        "UPDATE company_reports SET "
        "mentorship_grade = %s, "
        "work_environment_grade = %s, "
        "benefits_grade = %s, "
        "comment = %s "
        "WHERE student_id = %s AND offer_id = %s"
    )


def insert_company_report_query():
    return (
        "INSERT INTO company_reports "
        "(mentorship_grade, work_environment_grade, benefits_grade, comment, student_id, offer_id) "
        "VALUES (%s, %s, %s, %s, %s, %s)"
    )


def delete_company_report_query() -> LiteralString:
    return "DELETE FROM company_reports WHERE student_id = %s AND offer_id = %s"


def select_company_report_query() -> LiteralString:
    return "SELECT * FROM company_reports WHERE student_id = %s AND offer_id = %s"


def update_profile_picture_path_query(user_type: UserType) -> LiteralString:
    if user_type == UserType.STUDENT:
        return "UPDATE students SET profile_picture_path = %s WHERE id = %s;"
    elif user_type == UserType.COMPANY:
        return "UPDATE companies SET profile_picture_path = %s WHERE id = %s;"
    

def delete_profile_picture_path_query(user_type: UserType) -> LiteralString:
    if user_type == UserType.STUDENT:
        return "UPDATE students SET NULL = %s WHERE id = %s;"
    elif user_type == UserType.COMPANY:
        return "UPDATE companies SET NULL = %s WHERE id = %s;"
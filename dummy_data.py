import argparse
import psycopg as pg
from dataclasses import asdict, fields
from source.database import get_connection_string
from source.enums import Region, Status, Tables
from source.security import pwd_context
from tests.classes import (
    CompanyTest,
    OfferTest,
    StudentTest,
    ExperienceTest,
    ApplicationTest,
    SubjectTest,
    MotivationalLetterTest,
    StudentReportTest,
    CompanyReportTest,
    RegionTest,
)


def insert_regions() -> None:
    global_region = RegionTest(id=Region.GLOBAL.value, name="Global")
    europe_region = RegionTest(id=Region.EUROPE.value, name="Europe")
    asia_region = RegionTest(id=Region.ASIA.value, name="Asia")
    americas_region = RegionTest(id=Region.AMERICAS.value, name="Americas")
    
    insert_into_table(Tables.REGIONS, [
        global_region, 
        europe_region, 
        asia_region, 
        americas_region
    ])


def insert_companies() -> None:
    company_1 = CompanyTest(
        id=1, 
        email="company1@test.com", 
        password="123",
        hashed_password=pwd_context.hash("123"),
        name="Production Inc",
        field="Production",
        num_employees=100,
        year_founded=2000,
        website="production-inc.com.mk",
        description="The best company for production!",
    )
    company_2 = CompanyTest(
        id=2, 
        email="company2@test.com", 
        password="123",
        hashed_password=pwd_context.hash("123"),
        name="Marketing Inc",
        field="Marketing",
        num_employees=100,
        year_founded=2000,
        website="marketing-inc.com.mk",
        description="The best company for marketing!",
    )
    company_3 = CompanyTest(
        id=3, 
        email="company3@test.com", 
        password="123",
        hashed_password=pwd_context.hash("123"),
        name="Construction Inc",
        field="Construction",
        num_employees=100,
        year_founded=2000,
        website="construction-inc.com.mk",
        description="The best company for construction!",
    )
    insert_into_table("companies", [company_1, company_2, company_3])


def insert_offers() -> None:
    offer_1 = OfferTest(
        id=1, 
        salary=60000, 
        num_weeks=10, 
        field="Software Engineering", 
        deadline="2024-12-01", 
        requirements="Bachelor's degree in Computer Science or related field.", 
        responsibilities="Develop and maintain scalable web applications.", 
        company_id=1, 
        region_id=1,
    )
    offer_2 = OfferTest(
        id=2, 
        salary=50000, 
        num_weeks=20, 
        field="Marketing and Advertising", 
        deadline="2024-12-01", 
        requirements="Proficiency in Python, Java, or C++ programming languages.", 
        responsibilities="Collaborate with cross-functional teams to design solutions.", 
        company_id=1, 
        region_id=1,
    )
    offer_3 = OfferTest(
        id=3, 
        salary=40000, 
        num_weeks=30, 
        field="Data Science and Analytics", 
        deadline="2024-12-01", 
        requirements="Strong communication and teamwork skills.", 
        responsibilities="Conduct code reviews and ensure coding standards are met.", 
        company_id=1, 
        region_id=1,
    )
    offer_4 = OfferTest(
        id=4, 
        salary=30000, 
        num_weeks=40, 
        field="Project Management", 
        deadline="2024-12-01", 
        requirements="Minimum 2 years of experience in a similar role.", 
        responsibilities="Troubleshoot and debug software issues as they arise.", 
        company_id=2, 
        region_id=1,
    )
    offer_5 = OfferTest(
        id=5, 
        salary=20000, 
        num_weeks=50, 
        field="Mechanical Engineering", 
        deadline="2024-12-01", 
        requirements="Knowledge of agile development methodologies.", 
        responsibilities="Prepare technical documentation for developed systems.", 
        company_id=2, 
        region_id=1,
    )
    offer_6 = OfferTest(
        id=6, 
        salary=10000, 
        num_weeks=60, 
        field="Graphic Design and Multimedia", 
        deadline="2024-12-01", 
        requirements="Ability to work under pressure and meet tight deadlines.", 
        responsibilities="Assist in training junior team members and interns.", 
        company_id=2, 
        region_id=1,
    )
    offer_7 = OfferTest(
        id=7, 
        salary=70000, 
        num_weeks=70, 
        field="Human Resources and Recruitment", 
        deadline="2024-12-01", 
        requirements="Fluent in English, with excellent written and verbal skills.", 
        responsibilities="Participate in project planning and provide accurate estimates.", 
        company_id=3, 
        region_id=1,
    )
    offer_8 = OfferTest(
        id=8, 
        salary=80000, 
        num_weeks=80, 
        field="Finance and Investment Analysis", 
        deadline="2024-12-01", 
        requirements="Experience with cloud platforms such as AWS or Azure.", 
        responsibilities="Implement new features based on client requirements.", 
        company_id=3, 
        region_id=1,
    )
    offer_9 = OfferTest(
        id=9, 
        salary=90000, 
        num_weeks=90, 
        field="Healthcare and Medical Services", 
        deadline="2024-12-01", 
        requirements="Familiarity with data analysis and visualization tools.", 
        responsibilities="Monitor application performance and optimize for speed.", 
        company_id=3, 
        region_id=1,
    )
    insert_into_table(Tables.OFFERS, [
        offer_1, offer_2, offer_3,
        offer_4, offer_5, offer_6,
        offer_7, offer_8, offer_9,
    ])


def insert_students() -> None:
    student_1 = StudentTest(1, "student1@mail.com", "John Doe", "2000-01-01", "University of Istanbul", "Maritime Engineering", 180, 8.50, 1, "123", pwd_context.hash("123"))
    student_2 = StudentTest(2, "student2@mail.com", "Boris Watson", "2001-04-01", "University of Barcelona", "Quantum Mechanics", 180, 7.50, 1, "123", pwd_context.hash("123"))
    student_3 = StudentTest(3, "student3@mail.com", "Maria Rogers", "2002-05-01", "Technical University - Munich", "Financial Law", 180, 9.50, 1, "123", pwd_context.hash("123"))
    insert_into_table(Tables.STUDENTS, [student_1, student_2, student_3])


def insert_experiences() -> None:
    experience_1 = ExperienceTest(
        id=1,
        from_date="2020-01-01",
        to_date="2021-01-01",
        company="Tech Solutions Ltd",
        position="Software Developer Intern",
        description="Developed web applications and automated workflows.",
        student_id=1
    )
    experience_2 = ExperienceTest(
        id=2,
        from_date="2019-06-01",
        to_date="2019-12-31",
        company="Green Energy Corp",
        position="Junior Analyst",
        description="Analyzed energy consumption data and prepared reports.",
        student_id=2
    )
    experience_3 = ExperienceTest(
        id=3,
        from_date="2021-03-01",
        to_date="2022-03-01",
        company="Marketing Pros",
        position="Digital Marketing Specialist",
        description="Managed social media campaigns and SEO strategies.",
        student_id=3
    )
    experience_4 = ExperienceTest(
        id=4,
        from_date="2018-08-15",
        to_date="2020-08-15",
        company="Healthcare Innovations Inc",
        position="Research Assistant",
        description="Supported research on medical device innovations.",
        student_id=1
    )
    experience_5 = ExperienceTest(
        id=5,
        from_date="2020-05-01",
        to_date="2021-12-01",
        company="FinTech Solutions",
        position="Business Analyst Intern",
        description="Conducted market research and financial modeling.",
        student_id=2
    )
    experience_6 = ExperienceTest(
        id=6,
        from_date="2017-09-01",
        to_date="2018-06-01",
        company="Creative Studio X",
        position="Graphic Designer",
        description="Designed branding materials and promotional content.",
        student_id=3
    )
    experience_7 = ExperienceTest(
        id=7,
        from_date="2022-01-01",
        to_date="2023-01-01",
        company="AutoTech Corp",
        position="Mechanical Engineering Intern",
        description="Assisted in product testing and assembly line optimization.",
        student_id=1
    )
    experience_8 = ExperienceTest(
        id=8,
        from_date="2020-11-01",
        to_date="2022-04-01",
        company="Logistics Solutions Ltd",
        position="Supply Chain Coordinator",
        description="Monitored inventory levels and coordinated shipments.",
        student_id=2
    )
    experience_9 = ExperienceTest(
        id=9,
        from_date="2019-01-01",
        to_date="2020-01-01",
        company="Educational Outreach Org",
        position="Program Coordinator",
        description="Organized workshops and managed volunteer programs.",
        student_id=3
    )
    insert_into_table(Tables.EXPERIENCES, [
        experience_1, experience_2, experience_3,
        experience_4, experience_5, experience_6,
        experience_7, experience_8, experience_9,
    ])


def insert_subjects() -> None:
    subject_1 = SubjectTest(
        student_id=1,
        name="Mathematics",
        grade=6
    )
    subject_2 = SubjectTest(
        student_id=2,
        name="Physics",
        grade=7
    )
    subject_3 = SubjectTest(
        student_id=3,
        name="Economics",
        grade=8
    )
    subject_4 = SubjectTest(
        student_id=1,
        name="Statistics",
        grade=9
    )
    subject_5 = SubjectTest(
        student_id=2,
        name="Computer Science",
        grade=10
    )
    subject_6 = SubjectTest(
        student_id=3,
        name="Algorithms",
        grade=6
    )
    subject_7 = SubjectTest(
        student_id=1,
        name="History",
        grade=7
    )
    subject_8 = SubjectTest(
        student_id=2,
        name="Psychology",
        grade=8
    )
    subject_9 = SubjectTest(
        student_id=3,
        name="Chemistry",
        grade=9
    )
    insert_into_table(Tables.SUBJECTS, [
        subject_1, subject_2, subject_3,
        subject_4, subject_5, subject_6,
        subject_7, subject_8, subject_9,
    ])


def insert_motivational_letters() -> None:
    motivational_letter_1 = MotivationalLetterTest(
        student_id=1,
        about_me_section="I am a dedicated and curious student passionate about technology and innovation.",
        skills_section="Proficient in Python, JavaScript, and problem-solving; excellent communication skills.",
        looking_for_section="Seeking an internship to apply my software development skills in real-world projects."
    )
    motivational_letter_2 = MotivationalLetterTest(
        student_id=2,
        about_me_section="A highly motivated individual with a strong interest in business and analytics.",
        skills_section="Skilled in data analysis, financial modeling, and team collaboration.",
        looking_for_section="Looking for opportunities to grow as a business analyst in a dynamic company."
    )
    motivational_letter_3 = MotivationalLetterTest(
        student_id=3,
        about_me_section="An enthusiastic learner with a background in design and creative problem-solving.",
        skills_section="Expertise in graphic design, UI/UX principles, and Adobe Creative Suite.",
        looking_for_section="Aspiring to join a forward-thinking company to create impactful user experiences."
    )
    insert_into_table(Tables.MOTIVATIONAL_LETTERS, [motivational_letter_1, motivational_letter_2, motivational_letter_3])


def insert_applications() -> None:
    application_1 = ApplicationTest(student_id=1, offer_id=1, status=Status.WAITING.value)
    application_2 = ApplicationTest(student_id=2, offer_id=1, status=Status.WAITING.value)
    application_3 = ApplicationTest(student_id=3, offer_id=1, status=Status.WAITING.value)
    application_4 = ApplicationTest(student_id=1, offer_id=2, status=Status.WAITING.value)
    application_5 = ApplicationTest(student_id=2, offer_id=2, status=Status.WAITING.value)
    application_6 = ApplicationTest(student_id=3, offer_id=2, status=Status.WAITING.value)
    application_7 = ApplicationTest(student_id=1, offer_id=3, status=Status.WAITING.value)
    application_8 = ApplicationTest(student_id=2, offer_id=3, status=Status.WAITING.value)
    application_9 = ApplicationTest(student_id=3, offer_id=3, status=Status.WAITING.value)
    
    insert_into_table(Tables.APPLICATIONS, [
        application_1, application_2, application_3,
        application_4, application_5, application_6,
        application_7, application_8, application_9,
    ])


def insert_student_reports() -> None:
    # To be implemented
    student_report_1 = ...
    student_report_2 = ...
    student_report_3 = ...
    ...


def insert_company_reports() -> None:
    # To be implemented
    company_report_1 = ...
    company_report_2 = ...
    company_report_3 = ...
    ...


def insert_into_table(table_name: str, entities: list):
    connection_string = get_connection_string()
    connection = pg.connect(connection_string)

    for entity in entities:
        data = asdict(entity)    
        columns = [field.name for field in fields(entity) if field.name != "password"]
        values = tuple(data[column] for column in columns if column != "password")
        
        columns_str = ", ".join(columns)
        placeholders = ", ".join(["%s"] * len(columns))
        query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders});"

        try:
            with connection.cursor() as cur:
                cur.execute(query, values) # type: ignore
            connection.commit()
            print(f"Data inserted successfully into {table_name}.")
        except Exception as e:
            connection.rollback()
            print(f"Failed to insert data into {table_name}: {e}")


def delete_from_table(table_name: str):
    connection_string = get_connection_string()
    connection = pg.connect(connection_string)
    query = f"DELETE FROM {table_name};"

    try:
        with connection.cursor() as cur:
            cur.execute(query) # type: ignore
        connection.commit()
        print(f"All data deleted successfully from {table_name}.")
    except Exception as e:
        connection.rollback()
        print(f"Failed to delete data from {table_name}: {e}")
    finally:
        connection.close()


def insert_test_data() -> None:
    insert_regions()
    insert_companies()
    insert_offers()
    insert_students()
    insert_experiences()
    insert_subjects()
    insert_motivational_letters()
    insert_applications()
    # NOTE: To be implemented...
    # insert_student_reports()
    # insert_company_reports()


def remove_test_data() -> None:
    delete_from_table(Tables.COMPANY_REPORTS)
    delete_from_table(Tables.STUDENT_REPORTS)
    delete_from_table(Tables.APPLICATIONS)
    delete_from_table(Tables.MOTIVATIONAL_LETTERS)
    delete_from_table(Tables.SUBJECTS)
    delete_from_table(Tables.EXPERIENCES)
    delete_from_table(Tables.STUDENTS)
    delete_from_table(Tables.OFFERS)
    delete_from_table(Tables.COMPANIES)
    delete_from_table(Tables.REGIONS)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage test data.")
    parser.add_argument(
        "action",
        choices=["insert", "remove"],
        help="Specify whether to 'insert' or 'remove' test data."
    )
    args = parser.parse_args()

    if args.action == "insert":
        insert_test_data()
    elif args.action == "remove":
        remove_test_data()
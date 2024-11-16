from ..source.database import async_pool


def insert_regions() -> None:
    ...


def insert_companies() -> None:
    ...


def insert_offers() -> None:
    ...


def insert_students() -> None:
    ...


def insert_experiences() -> None:
    ...


def insert_subjects() -> None:
    ...


def insert_motivational_letters() -> None:
    ...


def insert_applications() -> None:
    ...


def insert_student_reports() -> None:
    ...


def insert_company_reports() -> None:
    ...


def insert_test_data() -> None:
    insert_regions()
    insert_companies()
    insert_offers()
    insert_students()
    insert_experiences()
    insert_subjects()
    insert_motivational_letters()
    insert_applications()
    insert_student_reports()
    insert_company_reports()


if __name__ == "__main__":
    print("Inserting test data")
    insert_test_data()
    print("Insertion complete")
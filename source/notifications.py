from source.queries import select_application_email_and_field_query, select_applications_emails_and_fields_query, select_offer_email_and_field_query
from .enums import Status
from .database import async_pool
from psycopg.rows import dict_row
from os import getenv
import smtplib


def send_email(to_address: str | list[str], subject: str, body: str) -> None:
    EMAIL_ADDRESS = getenv("EMAIL_ADDRESS", "")
    EMAIL_PASSWORD = getenv("EMAIL_PASSWORD", "")
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 465
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)        
        message = f"Subject: {subject}\n\n{body}"
        smtp.sendmail(EMAIL_ADDRESS, to_address, message)


def send_email_profile_created(to_address: str, name: str) -> None:
    subject = "Welcome - Profile Created"
    body = (
        f"Hello {name},\n\n"
        "Welcome to APLIPRAKSA!\n"
        "You have successfully created a profile on our platform.\n\n"
        "Sincerely,\n"
        "APLIPRAKSA Team"
    )
    send_email(to_address, subject, body)


def send_email_new_applicant(to_address: str, offer_field: str) -> None:
    subject = f"{offer_field} Offer - New Applicant"
    body = f"You have a new applicant for the '{offer_field}' offer."
    send_email(to_address, subject, body)


def send_email_cancelled_applicant(to_address: str, offer_field: str) -> None:
    subject = f"{offer_field} Offer - Applicant Cancellation"
    body = f"One of your applicants for the '{offer_field}' has cancelled their application"
    send_email(to_address, subject, body)


def send_email_application_update(to_address: str | list[str], offer_field: str, new_status: Status) -> None:
    subject = f"Application Status Update - {new_status.value}"
    body = f"Your application for the '{offer_field}' has been updated to {new_status.value}"
    send_email(to_address, subject, body)


async def notify_company_applicants_change(offer_id: int, is_new_applicant: bool):
    pool = async_pool()
    async with pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        query = select_offer_email_and_field_query()
        await cur.execute(query, [offer_id])
        record = await cur.fetchone()
    
    company_email = record["email"]
    offer_field = record["field"]
    
    if is_new_applicant:
        send_email_new_applicant(company_email, offer_field)
    else:
        send_email_cancelled_applicant(company_email, offer_field)


async def notify_student_application_status_change(student_id: int, offer_id: int, new_status: Status):
    pool = async_pool()
    async with pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        query = select_application_email_and_field_query()
        await cur.execute(query, [student_id, offer_id])
        record = await cur.fetchone()
    
    student_email = record["email"]
    offer_field = record["field"]
    send_email_application_update(student_email, offer_field, new_status)


async def notify_students_application_status_change(student_ids: list[int], offer_id: int, new_status: Status):
    pool = async_pool()
    async with pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        async with conn.transaction():
            query = select_applications_emails_and_fields_query()
            await cur.execute(query, [student_ids, offer_id])
            records = await cur.fetchall()
    
    student_emails = [item["email"] for item in records]
    offer_field = records[0]["field"]
    send_email_application_update(student_emails, offer_field, new_status)
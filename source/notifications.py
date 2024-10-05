from dotenv import load_dotenv
from os import getenv
import smtplib


def send_email(to_address: str, subject: str, body: str) -> None:
    load_dotenv()
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


def send_email_application_update(to_address: str, offer_field: str, new_status: str) -> None:
    subject = f"Application Status Update - {new_status}"
    body = f"Your application for the '{offer_field}' has been updated to {new_status}"
    send_email(to_address, subject, body)


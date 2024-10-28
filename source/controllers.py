from typing import Optional
from .schemas import (
    ApplicantRead,
    ExperienceCreate,
    ExperienceUpdate,
    MotivationalLetterRead,
    OfferUpdate,
    StudentCreate, 
    StudentUpdate, 
    StudentInDB, 
    StudentProfileRead, 
    StudentRead,
    CompanyCreate,
    CompanyRead,
    CompanyUpdate,
    CompanyInDB,
    OfferRead,
    OfferCreate,
    OfferBriefRead,
    OfferApplication,
    Subject,
    MotivationalLetter,
    StudentReport,
)
from .utils import (
    extract_file_offer,
    extract_subjects_from,
)
from .queries import (
    accept_student_query,
    delete_application_query,
    delete_company_query,
    delete_experience_query,
    delete_motivational_letter_query,
    delete_student_query,
    delete_student_report_query,
    delete_subject_query,
    insert_application_query,
    insert_company_query,
    insert_experience_query,
    insert_motivational_letter_query,
    insert_offer_query,
    insert_student_query,
    insert_student_report_query,
    insert_subject_query, 
    reject_students_query, 
    select_applicants_query,
    select_application_status_query,
    select_applications_query,
    select_company_offers_query,
    select_company_query,
    select_experience_student_id_query,
    select_motivational_letter_student_id_query,
    select_offer_company_id_query,
    select_offer_query,
    select_offers_query,
    select_student_experiences_query,
    select_student_report_query,
    select_student_reports_query,
    select_student_with_motivational_letter_query,
    select_student_subjects_query,
    select_subject_student_id_query,
    update_application_status_query,
    update_applications_waiting_query,
    update_company_query,
    update_experience_query,
    update_motivational_letter_query,
    update_offer_company_id_null_query,
    update_offer_query,
    update_student_query,
    update_student_report_query,
    update_subject_query
)
from .enums import Status, UserType
from .security import Token, get_token, pwd_context, authorize_user
from .database import async_pool
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import HTTPException, status
from psycopg.rows import dict_row, class_row
from psycopg import IntegrityError, AsyncCursor, AsyncConnection


# Token controllers


async def token_controller(user_type_param: str, form_data: OAuth2PasswordRequestForm) -> Token:
    email = form_data.username
    password = form_data.password
    user_type = UserType(user_type_param)
    return await get_token(email, password, user_type)


# Student controllers


async def student_post_controller(s: StudentCreate) -> None:
    hashed_password = pwd_context.hash(s.password)
    
    async with async_pool().connection() as conn:
        sql = insert_student_query()
        await conn.execute(sql, params=[
            s.email, 
            hashed_password, 
            s.name, 
            s.date_of_birth, 
            s.university, 
            s.major, 
            s.credits, 
            s.gpa,
            s.region_id,
        ])


async def student_put_controller(student_id: int, s: StudentUpdate, current_user) -> None:
    authorize_user(student_id, current_user, StudentInDB)
    
    async with async_pool().connection() as conn:
        sql = update_student_query()
        await conn.execute(sql, [
                s.email,
                s.name,
                s.date_of_birth,
                s.university,
                s.major,
                s.credits,
                s.gpa,
                student_id,
            ])
        

async def student_delete_controller(student_id: int, current_user) -> None:
    authorize_user(student_id, current_user, StudentInDB)
    
    async with async_pool().connection() as conn:
        sql = delete_student_query()
        await conn.execute(sql, [student_id])


async def student_profile_get_controller(student_id: int) -> StudentProfileRead:
    async with async_pool().connection() as conn:
        cur: AsyncCursor = conn.cursor(row_factory=dict_row)
        
        sql = select_student_with_motivational_letter_query()
        await cur.execute(sql, [student_id])
        student = await cur.fetchone()
        
        if student is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND)
        
        letter = MotivationalLetterRead(**student)
        student = StudentRead(**student, motivational_letter=letter)

        # Fetch student experiences
        sql = select_student_experiences_query()
        await cur.execute(sql, [student_id])
        experiences: list = await cur.fetchall()

        # Fetch student subjects
        sql = select_student_subjects_query()
        await cur.execute(sql, [student_id])
        subjects: list = await cur.fetchall()

        # Fetch student reports
        sql = select_student_reports_query()
        await cur.execute(sql, [student_id])
        reports: list = await cur.fetchall()

        student_profile = StudentProfileRead(
            subjects=subjects,
            experiences=experiences, 
            reports=reports,
            **student.model_dump(),
        )

        return student_profile
    

# Company controllers


async def company_post_controller(c: CompanyCreate) -> None:
    hashed_password = pwd_context.hash(c.password)
    async with async_pool().connection() as conn:
        sql = insert_company_query()
        await conn.execute(sql, params=[
                c.email,
                hashed_password,
                c.name,
                c.field,
                c.num_employees,
                c.year_founded,
                c.website,
            ])
        

async def company_get_controller(company_id: int) -> CompanyRead:
    async with async_pool().connection() as conn, conn.cursor(
        row_factory=class_row(CompanyRead)
    ) as cur:
        sql = select_company_query()
        await cur.execute(sql, [company_id])
        record = await cur.fetchone()
        if record is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND)
        return record
    

async def company_offers_get_controller(company_id: int) -> list[OfferRead]:
    async with async_pool().connection() as conn, conn.cursor(
        row_factory=class_row(OfferRead)
    ) as cur:
        sql = select_company_offers_query()
        await cur.execute(sql, [company_id])
        records = await cur.fetchall()
        return records
    

async def company_patch_controller(company_id: int, c: CompanyUpdate, current_user) -> None:
    authorize_user(company_id, current_user, CompanyInDB)
    
    async with async_pool().connection() as conn:
        sql = update_company_query()
        await conn.execute(sql, [
                c.email,
                c.name,
                c.field,
                c.num_employees,
                c.year_founded,
                c.website,
                company_id,
            ])
        

async def company_delete_controller(company_id: int, current_user) -> None:
    authorize_user(company_id, current_user, CompanyInDB)
    
    async with async_pool().connection() as conn:
        sql = delete_company_query()
        await conn.execute(sql, [company_id])


# Offer controllers


async def offer_post_controller(offer: OfferCreate, current_user) -> None:
    authorize_user(offer.company_id, current_user, CompanyInDB)

    async with async_pool().connection() as conn:
        sql = insert_offer_query()
        await conn.execute(sql, params=[
            offer.salary,
            offer.num_weeks,
            offer.field,
            offer.deadline,
            offer.requirements,
            offer.responsibilities,
            offer.company_id,
            offer.region_id,
        ])
        

async def offer_file_post_controller(offer_file_bytes: bytes, company_id: int, current_user) -> None:
    authorize_user(company_id, current_user, CompanyInDB)
    
    file_offer_info = extract_file_offer(offer_file_bytes)
    offer = OfferCreate(company_id=company_id, **file_offer_info)

    async with async_pool().connection() as conn:
        sql = insert_offer_query()
        await conn.execute(sql, params=[
            offer.salary,
            offer.num_weeks,
            offer.field,
            offer.deadline,
            offer.requirements,
            offer.responsibilities,
            offer.company_id,
            offer.region_id,
        ])
        

async def offers_get_controller(
    field: str | None,
    min_num_weeks: int,
    max_num_weeks: int,
    min_salary: int,
    max_salary: int,
    current_user: StudentInDB,
) -> list[OfferBriefRead]:
    authorize_user(current_user.id, current_user, StudentInDB)

    async with async_pool().connection() as conn, conn.cursor(
        row_factory=class_row(OfferBriefRead)
    ) as cur:
        sql = select_offers_query(field)
        parameters: list = [min_num_weeks, max_num_weeks, min_salary, max_salary, current_user.region_id]

        if field is not None:
            parameters.append(field)

        await cur.execute(sql, parameters)
        records = await cur.fetchall()
        return records
    

async def offer_get_controller(offer_id: int) -> OfferRead:
    async with async_pool().connection() as conn, conn.cursor(
        row_factory=class_row(OfferRead)
    ) as cur:
        sql = select_offer_query()
        await cur.execute(sql, [offer_id])
        record = await cur.fetchone()
        if record is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND)
        return record
    

async def offer_put_controller(offer_id: int, o: OfferUpdate, current_user) -> None:
    async with async_pool().connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        sql = select_offer_company_id_query()
        await cur.execute(sql, [offer_id])
        record = await cur.fetchone()
        
        if record is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND)

        authorize_user(record["company_id"], current_user, CompanyInDB)
        
        sql = update_offer_query()
        await conn.execute(sql, [
                o.salary,
                o.num_weeks,
                o.field,
                o.deadline,
                o.requirements,
                o.responsibilities,
                offer_id,
            ])
        

async def offer_delete_controller(offer_id: int, current_user) ->None:
    async with async_pool().connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        sql = select_offer_company_id_query()
        await cur.execute(sql, [offer_id])
        record = await cur.fetchone()

        if record is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND)
        
        authorize_user(record["company_id"], current_user, CompanyInDB)
        
        sql = update_offer_company_id_null_query()
        await conn.execute(sql, [offer_id])


# Experience controllers


async def experience_post_controller(e: ExperienceCreate, current_user) -> None:
    authorize_user(e.student_id, current_user, StudentInDB)

    async with async_pool().connection() as conn:
        sql = insert_experience_query()
        await conn.execute(sql, params=[
                e.from_date,
                e.to_date,
                e.company,
                e.position,
                e.description,
                e.student_id,
            ])
        

async def experience_patch_controller(
        experience_id: int, 
        s: ExperienceUpdate, 
        current_user
) -> None:
    async with async_pool().connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        sql = select_experience_student_id_query()
        await cur.execute(sql, [experience_id])
        record = await cur.fetchone()

        if record is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND)
        
        authorize_user(record["student_id"], current_user, StudentInDB)

        sql = update_experience_query()
        await conn.execute(sql, [
                s.from_date,
                s.to_date,
                s.company,
                s.position,
                s.description,
                experience_id,
            ])


async def experience_delete_controller(experience_id: int, current_user) -> None:
    async with async_pool().connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        sql = select_experience_student_id_query()
        await cur.execute(sql, [experience_id])
        record = await cur.fetchone()
        
        if record is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND)
        
        authorize_user(record["student_id"], current_user, StudentInDB)

        sql = delete_experience_query()
        await conn.execute(sql, [experience_id])


# Subject controllers


async def subject_post_controller(subject: Subject, current_user) -> None:
    authorize_user(subject.student_id, current_user, StudentInDB)

    async with async_pool().connection() as conn:
        sql = insert_subject_query()
        await conn.execute(sql, [
                subject.student_id, 
                subject.name,
                subject.grade,
        ])


async def subject_patch_controller(student_id: int, name: str, subject: Subject, current_user) -> None:
    pool = async_pool()
    async with pool.connection() as conn:
        cursor: AsyncCursor = conn.cursor(row_factory=dict_row)
        sql = select_subject_student_id_query()
        await cursor.execute(sql, [student_id, name])
        record = await cursor.fetchone()

        if record is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND)
        
        authorize_user(record["student_id"], current_user, StudentInDB)

        sql = update_subject_query()
        await conn.execute(sql, [
            subject.grade, 
            subject.student_id, 
            subject.name,
        ])


async def subject_delete_controller(student_id: int, name: str, current_user) -> None:
    pool = async_pool()
    async with pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        sql = select_subject_student_id_query()
        await cur.execute(sql, [student_id, name])
        record = await cur.fetchone()

        if record is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND)
        
        authorize_user(record["student_id"], current_user, StudentInDB)

        sql = delete_subject_query()
        await conn.execute(sql, [student_id, name])


# Application controllers


async def application_post_controller(
        student_id: int, 
        offer_id: int,
        current_user
) -> None:
    authorize_user(student_id, current_user, StudentInDB)

    # TODO:
    # Add logic to verify that the student is applying for 
    # an offer in his region or for a global offer
    
    async with async_pool().connection() as conn:
        sql = insert_application_query()
        try:
            await conn.execute(sql, [student_id, offer_id, Status.WAITING.value])
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        

async def applications_get_controller(student_id: int, current_user) -> list[OfferApplication]:
    authorize_user(student_id, current_user, StudentInDB)

    async with async_pool().connection() as conn, conn.cursor(
        row_factory=class_row(OfferApplication)
    ) as cur:
        sql = select_applications_query()
        await cur.execute(sql, [student_id])
        records = await cur.fetchall()
        return records
    

async def application_accept_controller(student_id: int, offer_id: int, current_user) -> dict:
    async with async_pool().connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        company_id = await retrieve_offer_company_id(offer_id, cur)
        authorize_user(company_id, current_user, CompanyInDB)
        
        async with conn.transaction():
            sql = accept_student_query()
            await cur.execute(sql, [student_id, offer_id])
            company_id = await cur.fetchone()
            accepted_student_id = company_id["student_id"]

            sql = reject_students_query()
            await cur.execute(sql, [student_id, offer_id])
            records = await cur.fetchall()
            rejected_student_ids = [item["student_id"] for item in records]
        
    return {
        "accepted_student_id": accepted_student_id, 
        "rejected_student_ids": rejected_student_ids
    }


async def retrieve_offer_company_id(offer_id: int, cursor: AsyncCursor):
    sql = select_offer_company_id_query()
    await cursor.execute(sql, [offer_id])
    record = await cursor.fetchone()
        
    if record is None:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Could not find company for offer."
            )
        
    return record["company_id"]


async def application_cancel_controller(student_id: int, offer_id: int, current_user) -> list[int]:
    authorize_user(student_id, current_user, StudentInDB)
    async with async_pool().connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        # Check the status of the given application
        sql = select_application_status_query()
        await cur.execute(sql, [student_id, offer_id])
        record = await cur.fetchone()
        
        if record is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND)
        
        application_status = record["status"]
        updated_student_ids = []

        # If the application is already accepted,
        # delete the given application and reset all
        # other applications for the same offer to status 'waiting'

        if application_status == Status.ACCEPTED.value:
            async with conn.transaction():
                sql = delete_application_query()
                await conn.execute(sql, [student_id, offer_id])
                sql = update_applications_waiting_query()
                await cur.execute(sql, [student_id, offer_id])
                records = await cur.fetchall()
                updated_student_ids = [item["student_id"] for item in records]
                
        # If the applicant is still waiting, 
        # just delete the application

        elif application_status == Status.WAITING.value:
            sql = delete_application_query()
            await cur.execute(sql, [student_id, offer_id])
        
    return updated_student_ids


async def applicants_get_controller(
    offer_id: int, 
    university: Optional[str],
    min_gpa: float,
    max_gpa: float,
    min_credits: int,
    max_credits: int,
    subjects_string: Optional[str],
    current_user,
) -> list[ApplicantRead]:
    
    async with async_pool().connection() as conn:
        applicant_cur = conn.cursor(row_factory=class_row(ApplicantRead))
        dict_cur = conn.cursor(row_factory=dict_row)
        
        query = select_offer_company_id_query()
        await dict_cur.execute(query, [offer_id])
        record = await dict_cur.fetchone()

        if record is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Could not find offer for the given id.",
            )
        
        authorize_user(record["company_id"], current_user, CompanyInDB)

        if subjects_string:
            subjects_list = extract_subjects_from(subjects_string)
        else:
            subjects_list = list()

        query, params = select_applicants_query(
            offer_id, 
            university,
            min_gpa,
            max_gpa,
            min_credits,
            max_credits,
            subjects_list,
        )
        await applicant_cur.execute(query, params)
        records = await applicant_cur.fetchall()

        return records
    

async def start_offer_controller(student_id: int, offer_id: int, current_user) -> None:
    async with async_pool().connection() as connection:
        await update_application_status(
            student_id,
            offer_id,
            Status.ACCEPTED,
            Status.ONGOING,
            connection,
            current_user,
        )


async def complete_offer_controller(student_id: int, offer_id: int, current_user) -> None:
    async with async_pool().connection() as connection:
        await update_application_status(
            student_id,
            offer_id,
            Status.ONGOING,
            Status.COMPLETED,
            connection,
            current_user,
        )


async def update_application_status(
    student_id: int, 
    offer_id: int, 
    required_status: Status, 
    new_status: Status,
    connection: AsyncConnection,
    current_user,
) -> None:
    """
    Generic function for updating the status of an application.
    """
    cur = connection.cursor(row_factory=dict_row)
    # Check that the offer exists in the system
    query = select_offer_company_id_query()
    await cur.execute(query, [offer_id])
    record = await cur.fetchone()

    if record is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Offer not found.")
    
    # Check if the offer is owned by the logged in user
    company_id = record["company_id"]
    authorize_user(company_id, current_user, CompanyInDB)

    # Check that the application has the correct current status
    query = select_application_status_query()
    await cur.execute(query, [student_id, offer_id])
    record = await cur.fetchone()
    current_status = record["status"] if record else None

    if current_status != required_status.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail=f"Cannot update offer with status {current_status}."
        )
    
    # Update the status of the application
    query = update_application_status_query(new_status)
    await connection.execute(query, [student_id, offer_id])
    

# Motivational Letter controllers


async def motivational_letter_post_controller(letter: MotivationalLetter, current_user) -> None:
    authorize_user(letter.student_id, current_user, StudentInDB)
    pool = async_pool()
    async with pool.connection() as conn:
        query = insert_motivational_letter_query()
        await conn.execute(query, [
            letter.student_id,
            letter.about_me_section,
            letter.skills_section,
            letter.looking_for_section,
        ])


async def motivational_letter_put_controller(letter: MotivationalLetter, current_user) -> None:
    pool = async_pool()
    async with (
        pool.connection() as conn,
        conn.cursor(row_factory=dict_row) as cur
    ):
        query = select_motivational_letter_student_id_query()
        await cur.execute(query, [letter.student_id])
        record = await cur.fetchone()

        if record is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND)
        
        authorize_user(letter.student_id, current_user, StudentInDB)

        query = update_motivational_letter_query()
        await conn.execute(query, [
            letter.about_me_section,
            letter.skills_section,
            letter.looking_for_section,
        ])


async def motivational_letter_delete_controller(student_id: int, current_user) -> None:
    pool = async_pool()
    async with (
        pool.connection() as conn,
        conn.cursor(row_factory=dict_row) as cur
    ):
        query = select_motivational_letter_student_id_query()
        await cur.execute(query, [student_id])
        record = await cur.fetchone()

        if record is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND)
        
        authorize_user(student_id, current_user, StudentInDB)

        query = delete_motivational_letter_query()
        await conn.execute(query, [student_id])


# Student Report controllers

async def upsert_student_report(student_report: StudentReport, current_user, is_update: bool) -> None:
    pool = async_pool()
    async with (
        pool.connection() as connection,
        connection.cursor(row_factory=dict_row) as cur
    ):
        # Verify that a company exists for the offer id
        query = select_offer_company_id_query()
        await cur.execute(query, [student_report.offer_id])
        record = await cur.fetchone()
        if record is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND)
        
        # Confirm if the current user has access to this operation
        company_id = record["company_id"]
        authorize_user(company_id, current_user, CompanyInDB)

        # Insert or update the student report
        if is_update:
            query = update_student_report_query()
        else:
            query = insert_student_report_query()
            await update_application_status(
                student_report.student_id,
                student_report.offer_id,
                Status.COMPLETED,
                Status.ARCHIVED,
                connection,
                current_user,
            )
        
        await connection.execute(query, [
            student_report.student_id,
            student_report.offer_id,
            student_report.overall_grade,
            student_report.technical_grade,
            student_report.communication_grade,
            student_report.comment,
        ])


async def student_report_post_controller(student_report: StudentReport, current_user) -> None:
    await upsert_student_report(student_report, current_user, is_update=False)


async def student_report_put_controller(student_report: StudentReport, current_user) -> None:
    await upsert_student_report(student_report, current_user, is_update=True)


async def student_report_delete_controller(student_id: int, offer_id: int, current_user):
    pool = async_pool()
    async with (
        pool.connection() as connection,
        connection.cursor(row_factory=dict_row) as cur
    ):
        # Verify that a company exists for the offer id
        query = select_offer_company_id_query()
        await cur.execute(query, [offer_id])
        record = await cur.fetchone()
        if record is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND)
        
        # Confirm if the current user has access to this operation
        company_id = record["company_id"]
        authorize_user(company_id, current_user, CompanyInDB)

        # Delete the student report
        query = delete_student_report_query()
        await connection.execute(query, [student_id, offer_id])

        # update application status from archived to completed
        await update_application_status(
            student_id,
            offer_id,
            Status.ARCHIVED,
            Status.COMPLETED,
            connection,
            current_user,
        )


async def student_report_get_controller(student_id: int, offer_id: int) -> StudentReport:
    async with async_pool().connection() as conn:
        cur = conn.cursor(row_factory=class_row(StudentReport))
        query = select_student_report_query()
        await cur.execute(query, [student_id, offer_id])
        record = await cur.fetchone()

        if record is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND)
        
        return record
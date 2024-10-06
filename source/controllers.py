from .schemas import (
    ApplicantRead,
    ExperienceCreate,
    ExperienceUpdate,
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
)
from .utils import (
    accept_student_query,
    delete_application_query,
    delete_company_query,
    delete_experience_query,
    delete_student_query,
    insert_application_query,
    insert_company_query,
    insert_experience_query,
    insert_offer_query,
    insert_student_query, 
    reject_students_query, 
    select_applicants_query,
    select_application_status_query,
    select_applications_query,
    select_company_offers_query,
    select_company_query,
    select_experience_student_id_query,
    select_offer_company_id_query,
    select_offer_query,
    select_offers_query,
    select_student_experiences_query,
    select_student_query,
    update_applications_waiting_query,
    update_company_query,
    update_experience_query,
    update_offer_company_id_null_query,
    update_offer_query,
    update_student_query
)
from .enums import Status, UserType
from .security import Token, get_token, pwd_context, authorize_user
from .database import async_pool
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import HTTPException, status
from psycopg.rows import dict_row, class_row
from psycopg import IntegrityError, AsyncCursor


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
        cur = conn.cursor(row_factory=dict_row)
        
        sql = select_student_query()
        await cur.execute(sql, [student_id])
        record = await cur.fetchone()
        
        if record is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND)
        
        student = StudentRead(**record)

        sql = select_student_experiences_query()
        await cur.execute(sql, [student_id])
        experiences: list = await cur.fetchall()

        student_profile = StudentProfileRead(experiences=experiences, **student.model_dump())

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


async def offer_post_controller(o: OfferCreate, current_user) -> None:
    authorize_user(o.company_id, current_user, CompanyInDB)

    async with async_pool().connection() as conn:
        sql = insert_offer_query()
        await conn.execute(sql, params=[
                o.salary,
                o.num_weeks,
                o.field,
                o.deadline,
                o.requirements,
                o.responsibilities,
                o.company_id,
                o.region_id,
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


async def applicants_get_controller(offer_id: int, current_user) -> list[ApplicantRead]:
    async with async_pool().connection() as conn:
        applicant_cur = conn.cursor(row_factory=class_row(ApplicantRead))
        dict_cur = conn.cursor(row_factory=dict_row)
        
        sql = select_offer_company_id_query()
        await dict_cur.execute(sql, [offer_id])
        record = await dict_cur.fetchone()

        if record is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Could not find offer for the given id.",
            )
        
        authorize_user(record["company_id"], current_user, CompanyInDB)

        sql = select_applicants_query()
        await applicant_cur.execute(sql, [offer_id])
        records = await applicant_cur.fetchall()
        return records
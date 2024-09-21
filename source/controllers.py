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
from .enums import Status, UserType
from .security import Token, get_token, pwd_context, authorize_user
from .database import get_async_pool
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import HTTPException, status
from psycopg.rows import dict_row, class_row
from psycopg import IntegrityError


# Token controllers


async def token_controller(user_type_param: str, form_data: OAuth2PasswordRequestForm) -> Token:
    email = form_data.username
    password = form_data.password
    user_type = UserType(user_type_param)
    return await get_token(email, password, user_type)


# Student controllers


async def student_post_controller(s: StudentCreate) -> None:
    hashed_password = pwd_context.hash(s.password)
    
    async with get_async_pool().connection() as conn:
        sql = """
            INSERT INTO students 
            (email, hashed_password, name, date_of_birth, university, major, credits, gpa, region_id) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
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
    
    async with get_async_pool().connection() as conn:
        sql = """UPDATE students SET 
                email=%s, name=%s, date_of_birth=%s, university=%s, 
                major=%s, credits=%s, gpa=%s WHERE id=%s 
                RETURNING *;"""
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
    
    async with get_async_pool().connection() as conn:
        sql = "DELETE FROM students WHERE id = %s"
        await conn.execute(sql, [student_id])


async def student_profile_get_controller(student_id: int) -> StudentProfileRead:
    async with get_async_pool().connection() as conn:
        cur = conn.cursor(row_factory=dict_row)
        
        sql = "SELECT * FROM students WHERE id = %s;"
        await cur.execute(sql, [student_id])
        record = await cur.fetchone()
        
        if record is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND)
        
        student = StudentRead(**record)

        sql = "SELECT * FROM experiences WHERE student_id = %s;"
        await cur.execute(sql, [student_id])
        experiences: list = await cur.fetchall()

        student_profile = StudentProfileRead(experiences=experiences, **student.model_dump())

        return student_profile
    

# Company controllers


async def company_post_controller(c: CompanyCreate) -> None:
    hashed_password = pwd_context.hash(c.password)
    async with get_async_pool().connection() as conn:
        sql = """INSERT INTO companies 
                (email, hashed_password, name, field, num_employees, year_founded, website) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)"""
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
    async with get_async_pool().connection() as conn, conn.cursor(
        row_factory=class_row(CompanyRead)
    ) as cur:
        sql = "SELECT * FROM companies WHERE id = %s;"
        await cur.execute(sql, [company_id])
        record = await cur.fetchone()
        if record is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND)
        return record
    

async def company_offers_get_controller(company_id: int) -> list[OfferRead]:
    async with get_async_pool().connection() as conn, conn.cursor(
        row_factory=class_row(OfferRead)
    ) as cur:
        sql = (
            "SELECT o.id, o.salary, o.num_weeks, o.field, o.deadline, o.requirements, o.responsibilities, o.company_id, r.name as region "
            "FROM offers as o "
            "JOIN regions as r ON o.region_id = r.id "
            "WHERE o.company_id = %s;"
        )
        await cur.execute(sql, [company_id])
        records = await cur.fetchall()
        return records
    

async def company_patch_controller(company_id: int, c: CompanyUpdate, current_user) -> None:
    authorize_user(company_id, current_user, CompanyInDB)
    
    async with get_async_pool().connection() as conn:
        sql = (
            "UPDATE companies SET "
            "email=%s, name=%s, field=%s, num_employees=%s, year_founded=%s, website=%s "
            "WHERE id=%s RETURNING *;"
        )
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
    
    async with get_async_pool().connection() as conn:
        sql = "DELETE FROM companies WHERE id = %s"
        await conn.execute(sql, [company_id])


# Offer controllers


async def offer_post_controller(o: OfferCreate, current_user) -> None:
    authorize_user(o.company_id, current_user, CompanyInDB)

    async with get_async_pool().connection() as conn:
        sql = """INSERT INTO offers 
                (salary, num_weeks, field, deadline, requirements, responsibilities, company_id, region_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
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

    async with get_async_pool().connection() as conn, conn.cursor(
        row_factory=class_row(OfferBriefRead)
    ) as cur:
        sql = (
            "SELECT o.id, o.salary, o.num_weeks, o.field, o.deadline, r.name as region, c.name AS company_name "
            "FROM offers AS o "
            "JOIN companies AS c ON o.company_id = c.id "
            "JOIN regions AS r ON o.region_id = r.id "
            "WHERE o.num_weeks >= %s AND o.num_weeks <= %s "
            "AND o.salary >= %s AND o.salary <= %s "
            "AND (r.id = %s OR r.name = 'Global')"
        )
        parameters: list = [min_num_weeks, max_num_weeks, min_salary, max_salary, current_user.region_id]

        if field is not None:
            sql += " AND o.field = %s"
            parameters.append(field)

        print(sql)
        print(parameters)

        await cur.execute(sql, parameters)
        records = await cur.fetchall()
        return records
    

async def offer_get_controller(offer_id: int) -> OfferRead:
    async with get_async_pool().connection() as conn, conn.cursor(
        row_factory=class_row(OfferRead)
    ) as cur:
        sql = (
            "SELECT o.id, o.salary, o.num_weeks, o.field, o.deadline, o.requirements, o.responsibilities, o.company_id, r.name as region "
            "FROM offers as o "
            "JOIN regions as r ON o.region_id = r.id "
            "WHERE o.id = %s;"
        )
        await cur.execute(sql, [offer_id])
        record = await cur.fetchone()
        if record is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND)
        return record
    

async def offer_put_controller(offer_id: int, o: OfferUpdate, current_user) -> None:
    async with get_async_pool().connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        sql = "SELECT company_id FROM offers WHERE id = %s;"
        await cur.execute(sql, [offer_id])
        record = await cur.fetchone()
        
        if record is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND)

        authorize_user(record["company_id"], current_user, CompanyInDB)
        
        sql = """UPDATE offers SET 
                salary=%s, num_weeks=%s, field=%s, deadline=%s, requirements=%s, responsibilities=%s 
                WHERE id=%s 
                RETURNING *;"""
        
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
    async with get_async_pool().connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        sql = "SELECT company_id FROM offers WHERE id = %s;"
        await cur.execute(sql, [offer_id])
        record = await cur.fetchone()

        if record is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND)
        
        authorize_user(record["company_id"], current_user, CompanyInDB)
        
        sql = "UPDATE offers SET company_id = NULL WHERE id = %s"
        await conn.execute(sql, [offer_id])


# Experience controllers


async def experience_post_controller(e: ExperienceCreate, current_user) -> None:
    authorize_user(e.student_id, current_user, StudentInDB)

    async with get_async_pool().connection() as conn:
        sql = """INSERT INTO experiences 
                (from_date, to_date, company, position, description, student_id) 
                VALUES (%s, %s, %s, %s, %s, %s)"""
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
    async with get_async_pool().connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        sql = "SELECT student_id FROM experiences WHERE id = %s"
        await cur.execute(sql, [experience_id])
        record = await cur.fetchone()

        if record is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND)
        
        authorize_user(record["student_id"], current_user, StudentInDB)

        sql = """
            UPDATE experiences SET 
            from_date=%s, to_date=%s, company=%s, position=%s, description=%s 
            WHERE id=%s 
            RETURNING *;
        """
        await conn.execute(sql, [
                s.from_date,
                s.to_date,
                s.company,
                s.position,
                s.description,
                experience_id,
            ])


async def experience_delete_controller(experience_id: int, current_user) -> None:
    async with get_async_pool().connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        sql = "SELECT student_id FROM experiences WHERE id = %s"
        await cur.execute(sql, [experience_id])
        record = await cur.fetchone()
        
        if record is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND)
        
        authorize_user(record["student_id"], current_user, StudentInDB)

        sql = "DELETE FROM experiences WHERE id = %s"
        await conn.execute(sql, [experience_id])


# Application controllers


async def application_post_controller(student_id: int, offer_id: int, current_user) -> None:
    authorize_user(student_id, current_user, StudentInDB)
    
    # TODO: Fix error-500 (for invalid offer_id)?

    async with get_async_pool().connection() as conn:
        sql = "INSERT INTO applications (student_id, offer_id, status) VALUES (%s, %s, %s)"
        try:
            await conn.execute(sql, [student_id, offer_id, Status.WAITING.value])
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


async def applications_get_controller(student_id: int, current_user) -> list[OfferApplication]:
    authorize_user(student_id, current_user, StudentInDB)

    async with get_async_pool().connection() as conn, conn.cursor(
        row_factory=class_row(OfferApplication)
    ) as cur:
        sql = """
            SELECT 
                o.field, o.salary, o.num_weeks, 
                a.status, a.student_id, a.offer_id
            FROM offers o
            JOIN applications a ON o.id = a.offer_id
            WHERE a.student_id = %s;
        """
        await cur.execute(sql, [student_id])
        records = await cur.fetchall()
        return records
    

async def application_accept_controller(student_id: int, offer_id: int, current_user) -> None:
    async with get_async_pool().connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        sql = "SELECT company_id FROM offers WHERE id = %s"
        await cur.execute(sql, [offer_id])
        record = await cur.fetchone()
        
        if record is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND)
        
        authorize_user(record["company_id"], current_user, CompanyInDB)
        
        async with conn.transaction():
            sql = """
                UPDATE applications SET status = 1
                WHERE student_id = %s AND offer_id = %s AND status = 0;
            """
            await conn.execute(sql, [student_id, offer_id])
            sql = """
                UPDATE applications SET status = 2
                WHERE student_id <> %s AND offer_id = %s AND status = 0;
            """
            await conn.execute(sql, [student_id, offer_id])
        

async def application_cancel_controller(student_id: int, offer_id: int, current_user) -> None:
    authorize_user(student_id, current_user, StudentInDB)

    async with get_async_pool().connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        # Check the status of the given application
        sql = "SELECT status FROM applications WHERE student_id=%s AND offer_id=%s;"
        await cur.execute(sql, [student_id, offer_id])
        record = await cur.fetchone()
        
        if record is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND)
        
        application_status = record["status"]

        # If the application is already accepted,
        # delete the given application and reset all
        # other applications for the same offer to status 'waiting'
        if application_status == Status.ACCEPTED.value:
            async with conn.transaction():
                sql = """
                    DELETE FROM applications
                    WHERE student_id=%s AND offer_id=%s;
                """
                await conn.execute(sql, [student_id, offer_id])
                sql = """
                    UPDATE applications SET status = 0 
                    WHERE student_id <> %s AND offer_id = %s;
                """
                await conn.execute(sql, [student_id, offer_id])
                
        # If the applicant is still waiting, 
        # just delete the application
        elif application_status == Status.WAITING.value:
            sql = "DELETE FROM applications WHERE student_id=%s AND offer_id=%s;"
            await cur.execute(sql, [student_id, offer_id])


async def applicants_get_controller(offer_id: int, current_user) -> list[ApplicantRead]:
    async with get_async_pool().connection() as conn:
        applicant_cur = conn.cursor(row_factory=class_row(ApplicantRead))
        dict_cur = conn.cursor(row_factory=dict_row)
        
        sql = "SELECT company_id FROM offers WHERE id = %s"
        await dict_cur.execute(sql, [offer_id])
        record = await dict_cur.fetchone()

        if record is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND)
        
        authorize_user(record["company_id"], current_user, CompanyInDB)

        sql = """
            SELECT 
                s.id, s.email, s.name, s.date_of_birth, 
                s.university, s.major, s.credits, s.gpa, 
                a.status
            FROM students s
            JOIN applications a ON s.id = a.student_id
            WHERE a.offer_id = %s;
        """
        await applicant_cur.execute(sql, [offer_id])
        records = await applicant_cur.fetchall()
        return records
from .utils import pwd_context
from .enums import Status
from .database import get_async_pool
from .schemas import (
    StudentCreate,
    StudentRead,
    StudentUpdate,
    CompanyCreate,
    CompanyRead,
    CompanyUpdate,
    OfferCreate,
    OfferRead,
    OfferUpdate,
    ExperienceCreate,
    ExperienceRead,
    ExperienceUpdate,
    StudentProfile,
    ApplicationRead,
)
from fastapi import APIRouter, status, HTTPException, Query
from psycopg.rows import class_row, dict_row
from typing import Annotated


router = APIRouter()
pool = get_async_pool()


@router.post("/students", status_code=status.HTTP_201_CREATED, tags=["students"])
async def student_post(s: StudentCreate):
    hashed_password = pwd_context.hash(s.password)
    async with pool.connection() as conn:
        sql = """INSERT INTO students                                               
                (email, hashed_password, name, age, 
                university, major, credits, gpa)    
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
        await conn.execute(
            sql,
            params=[
                s.email,
                hashed_password,
                s.name,
                s.age,
                s.university,
                s.major,
                s.credits,
                s.gpa,
            ],
        )


@router.put("/students/{student_id}", tags=["students"])
async def student_patch(student_id: int, s: StudentUpdate):
    async with pool.connection() as conn:
        sql = "UPDATE students SET                                              \
            email=%s, name=%s, age=%s, university=%s, major=%s, credits=%s, gpa=%s   \
            WHERE id=%s RETURNING *;"
        await conn.execute(
            sql,
            [
                s.email,
                s.name,
                s.age,
                s.university,
                s.major,
                s.credits,
                s.gpa,
                student_id,
            ],
        )


@router.delete("/students/{student_id}", tags=["students"])
async def student_delete(student_id: int):
    async with pool.connection() as conn:
        sql = "DELETE FROM students WHERE id = %s"
        await conn.execute(sql, [student_id])


@router.get("/student/profile/{student_id}", response_model=StudentProfile, tags=["students"])
async def student_profile_get(student_id: int):
    async with pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        sql = "SELECT * FROM students WHERE id = %s;"
        await cur.execute(sql, [student_id])
        record = await cur.fetchone()
        if record is None:
            raise HTTPException(404)
        student = StudentRead(**record)

        sql = "SELECT * FROM experiences WHERE student_id = %s;"
        await cur.execute(sql, [student_id])
        experiences: list = await cur.fetchall()

        student_profile = StudentProfile(experiences=experiences, **student.dict())

        return student_profile


""" Routes for COMPANIES """


@router.post("/companies", status_code=status.HTTP_201_CREATED, tags=["companies"])
async def company_post(c: CompanyCreate):
    hashed_password = pwd_context.hash(c.password)
    async with pool.connection() as conn:
        sql = "INSERT INTO companies                                                    \
            (email, hashed_password, name, field, num_employees, year_founded, website) \
            VALUES (%s, %s, %s, %s, %s, %s, %s)"
        await conn.execute(
            sql,
            params=[
                c.email,
                hashed_password,
                c.name,
                c.field,
                c.num_employees,
                c.year_founded,
                c.website,
            ],
        )


@router.get("/companies/{company_id}", response_model=CompanyRead, tags=["companies"])
async def company_get(company_id: int):
    async with pool.connection() as conn, conn.cursor(
        row_factory=class_row(CompanyRead)
    ) as cur:
        sql = "SELECT * FROM companies WHERE id = %s;"
        await cur.execute(sql, [company_id])
        record = await cur.fetchone()
        if record is None:
            raise HTTPException(404)
        return record


@router.get(
    "/companies/{company_id}/offers", response_model=list[OfferRead], tags=["companies"]
)
async def company_offers_get(company_id: int):
    async with pool.connection() as conn, conn.cursor(
        row_factory=class_row(OfferRead)
    ) as cur:
        sql = "SELECT * FROM offers WHERE company_id = %s;"
        await cur.execute(sql, [company_id])
        records = await cur.fetchall()
        return records


@router.put("/companies/{company_id}", tags=["companies"])
async def company_patch(company_id: int, c: CompanyUpdate):
    async with pool.connection() as conn:
        sql = """UPDATE companies SET                                                 
            email=%s, name=%s, field=%s, num_employees=%s, year_founded=%s, website=%s
            WHERE id=%s RETURNING *;"""
        await conn.execute(
            sql,
            [
                c.email,
                c.name,
                c.field,
                c.num_employees,
                c.year_founded,
                c.website,
                company_id,
            ],
        )


@router.delete("/companies/{company_id}", tags=["companies"])
async def company_delete(company_id: int):
    async with pool.connection() as conn:
        sql = "DELETE FROM companies WHERE id = %s"
        await conn.execute(sql, [company_id])


""" Routes for OFFERS """


@router.post("/offers", status_code=status.HTTP_201_CREATED, tags=["offers"])
async def offer_post(o: OfferCreate):
    async with pool.connection() as conn:
        sql = "INSERT INTO offers                                                   \
            (salary, num_weeks, field, deadline, requirements, responsibilities, company_id)    \
            VALUES (%s, %s, %s, %s, %s, %s, %s)"
        await conn.execute(
            sql,
            params=[
                o.salary,
                o.num_weeks,
                o.field,
                o.deadline,
                o.requirements,
                o.responsibilities,
                o.company_id,
            ],
        )


@router.get("/offers", response_model=list[OfferRead], tags=["offers"])
async def offers_get(
    field: str | None = None,
    min_num_weeks: int | None = None,
    max_num_weeks: int | None = None,
    min_salary: int | None = None,
    max_salary: int | None = None,
):
    """ Returns all offers that satisfy the given query parameters """
    async with pool.connection() as conn, conn.cursor(
        row_factory=class_row(OfferRead)
    ) as cur:
        sql = "SELECT * FROM offers WHERE 1=1"

        parameters = []

        """ 
        Builds the SQL query based on the given parameters.
        Also builds the list with the appropriate parameters.  
        """

        if field is not None:
            sql += " AND field = %s"
            parameters.append(field)
        elif min_num_weeks is not None:
            sql += " AND min_num_weeks >= %s"
            parameters.append(min_num_weeks)
        elif max_num_weeks is not None:
            sql += " AND max_num_weeks <= %s"
            parameters.append(max_num_weeks)
        elif min_salary is not None:
            sql += " AND min_salary = %s"
            parameters.append(min_salary)
        elif max_salary is not None:
            sql += " AND max_salary = %s"
            parameters.append(max_salary)

        await cur.execute(sql, parameters)
        records = await cur.fetchall()
        return records


@router.get("/offers/{offer_id}", response_model=OfferRead, tags=["offers"])
async def offer_get(offer_id: int):
    async with pool.connection() as conn, conn.cursor(
        row_factory=class_row(OfferRead)
    ) as cur:
        sql = "SELECT * FROM offers WHERE id = %s;"
        await cur.execute(sql, [offer_id])
        record = await cur.fetchone()
        if record is None:
            raise HTTPException(404)
        return record


@router.put("/offers/{offer_id}", tags=["offers"])
async def offer_put(offer_id: int, s: OfferUpdate):
    async with pool.connection() as conn:
        sql = "UPDATE offers SET                                                                    \
            salary=%s, num_weeks=%s, field=%s, deadline=%s, requirements=%s, responsibilities=%s    \
            WHERE id=%s RETURNING *;"
        await conn.execute(
            sql,
            [
                s.salary,
                s.num_weeks,
                s.field,
                s.deadline,
                s.requirements,
                s.responsibilities,
                offer_id,
            ],
        )


@router.delete("/offers/{offer_id}", tags=["offers"])
async def offer_delete(offer_id: int):
    async with pool.connection() as conn:
        sql = "DELETE FROM offers WHERE id = %s"
        await conn.execute(sql, [offer_id])


""" Routes for EXPERIENCES """


@router.post("/experiences", status_code=status.HTTP_201_CREATED, tags=["experiences"])
async def experience_post(e: ExperienceCreate):
    async with pool.connection() as conn:
        sql = "INSERT INTO experiences                                                   \
            (from_date, to_date, company, position, description, student_id)    \
            VALUES (%s, %s, %s, %s, %s, %s)"
        await conn.execute(
            sql,
            params=[
                e.from_date,
                e.to_date,
                e.company,
                e.position,
                e.description,
                e.student_id,
            ],
        )


@router.put("/experiences/{experience_id}", tags=["experiences"])
async def experience_patch(experience_id: int, s: ExperienceUpdate):
    async with pool.connection() as conn:
        sql = "UPDATE experiences SET                                           \
            from_date=%s, to_date=%s, company=%s, position=%s, description=%s   \
            WHERE id=%s RETURNING *;"
        await conn.execute(
            sql,
            [
                s.from_date,
                s.to_date,
                s.company,
                s.position,
                s.description,
                experience_id,
            ],
        )


@router.delete("/experiences/{experience_id}", tags=["experiences"])
async def experience_delete(experience_id: int):
    async with pool.connection() as conn:
        sql = "DELETE FROM experiences WHERE id = %s"
        await conn.execute(sql, [experience_id])


""" Routes for APPLICATIONS """


@router.post("/applications/apply/{student_id}/{offer_id}", tags=["applications"])
async def application_post(student_id: int, offer_id: int):
    async with pool.connection() as conn:
        sql = "INSERT INTO applications (student_id, offer_id, status) VALUES (%s, %s, %s)"
        await conn.execute(sql, [student_id, offer_id, Status.WAITING.value])


@router.get(
    "/applications/view/{student_id}",
    response_model=list[ApplicationRead],
    tags=["applications"],
)
async def applications_get(student_id: int):
    async with pool.connection() as conn, conn.cursor(
        row_factory=class_row(ApplicationRead)
    ) as cur:
        sql = "SELECT student_id, offer_id, status FROM applications WHERE student_id = %s;"
        await cur.execute(sql, [student_id])
        records = await cur.fetchall()
        return records


@router.patch("/applications/accept/{student_id}/{offer_id}", tags=["applications"])
async def application_accept(student_id: int, offer_id: int):
    """
    If a student has status - waiting for a given application,
    set his his status to - accepted. Change all other applications
    to status - rejected.
    """
    async with pool.connection() as conn:
        sql = "CALL accept_student(%s, %s);"
        await conn.execute(sql, [student_id, offer_id])


@router.delete("/applications/cancel/{student_id}/{offer_id}", tags=["applications"])
async def application_cancel(student_id: int, offer_id: int):
    """
    If a student is still waiting for his application, simply delete his application.
    If the student's application has been accepted, then delete his application and
    reset all other applications (for the same offer) to status - waiting.
    """
    async with pool.connection() as conn:
        sql = "CALL cancel_application(%s, %s);"
        await conn.execute(sql, [student_id, offer_id])


@router.get("/applications/applicants/{offer_id}", tags=["applications"])
async def applicants_get(offer_id: int):
    """Get all student-applicants that have applied for the given offer."""
    async with pool.connection() as conn, conn.cursor(
        row_factory=class_row(StudentRead)
    ) as cur:
        sql = "SELECT * FROM applicants(%s)"
        await cur.execute(sql, [offer_id])
        records = await cur.fetchall()
        return records


""" Possibly unnecessary? """
# @router.get("/students", response_model=list[StudentRead], tags=["students"])
# async def students_get():
#     async with pool.connection() as conn, conn.cursor(
#         row_factory=class_row(StudentRead)
#     ) as cur:
#         sql = "SELECT * FROM students;"
#         await cur.execute(sql)
#         records = await cur.fetchall()
#         return records


""" Possibly unnecessary? """
# @router.get("/students/{student_id}", response_model=StudentRead, tags=["students"])
# async def student_get(student_id: int):
#     async with pool.connection() as conn, conn.cursor(row_factory=class_row(StudentRead)) as cur:
#         sql = "SELECT * FROM students WHERE id = %s;"
#         await cur.execute(sql, [student_id])
#         record = await cur.fetchone()
#         if record is None:
#             raise HTTPException(404)
#         return record


""" Perhaps unnecessary? """
# @router.get("/experiences", response_model=list[ExperienceRead], tags=["experiences"])
# async def experiences_get():
#     async with pool.connection() as conn, conn.cursor(row_factory=class_row(ExperienceRead)) as cur:
#         sql = "SELECT * FROM experiences;"
#         await cur.execute(sql)
#         records = await cur.fetchall()
#         return records


""" Perhaps unnecessary? """
# @router.get("/experiences/{experience_id}", response_model=ExperienceRead, tags=["experiences"])
# async def experience_get(experience_id: int):
#     async with pool.connection() as conn, conn.cursor(row_factory=class_row(ExperienceRead)) as cur:
#         sql = "SELECT * FROM experiences WHERE id = %s;"
#         await cur.execute(sql, [experience_id])
#         record = await cur.fetchone()
#         if record is None:
#             raise HTTPException(404)
#         return record
from .database import get_async_pool
from .schemas import (
    StudentCreate, StudentRead, StudentUpdate,
    CompanyCreate, CompanyRead, CompanyUpdate,
    OfferCreate, OfferRead, OfferUpdate,
)
from fastapi import APIRouter, status, HTTPException
from psycopg.rows import class_row


router = APIRouter()
pool = get_async_pool()

@router.post("/students", status_code=status.HTTP_201_CREATED, tags=["student"])
async def student_post(s: StudentCreate):
    async with pool.connection() as conn:
        sql = "INSERT INTO students                                                 \
            (email, hashed_password, name, age, university, major, credits, gpa)    \
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        await conn.execute(sql, params=[
            s.email, s.password, s.name, s.age, s.university, s.major, s.credits, s.gpa,
        ])


@router.get("/students", response_model=list[StudentRead], tags=["student"])
async def students_get():
    async with pool.connection() as conn, conn.cursor(row_factory=class_row(StudentRead)) as cur:
        sql = "SELECT * FROM students;"
        await cur.execute(sql)
        records = await cur.fetchall()
        return records


@router.get("/students/{student_id}", response_model=StudentRead, tags=["student"])
async def student_get(student_id: int):
    async with pool.connection() as conn, conn.cursor(row_factory=class_row(StudentRead)) as cur:
        sql = "SELECT * FROM students WHERE id = %s;"
        await cur.execute(sql, [student_id])
        record = await cur.fetchone()
        if record is None:
            raise HTTPException(404)
        return record


@router.put("/students/{student_id}", tags=["student"])
async def student_patch(student_id: int, s: StudentUpdate):
    async with pool.connection() as conn:
        sql = "UPDATE students SET                                              \
            email=%s, name=%s, age=%s, university=%s, major=%s, credits=%s, gpa=%s   \
            WHERE id=%s RETURNING *;"
        await conn.execute(sql, [s.email, s.name, s.age, s.university, s.major, s.credits, s.gpa, student_id])
    

@router.delete("/students/{student_id}", tags=["student"])
async def student_delete(student_id: int):
    async with pool.connection() as conn:
        sql = "DELETE FROM students WHERE id = %s"
        await conn.execute(sql, [student_id])


""" Routes for COMPANIES """

@router.post("/companies", status_code=status.HTTP_201_CREATED, tags=["company"])
async def company_post(c: CompanyCreate):
    async with pool.connection() as conn:
        sql = "INSERT INTO companies                                                    \
            (email, hashed_password, name, field, num_employees, year_founded, website) \
            VALUES (%s, %s, %s, %s, %s, %s, %s)"
        await conn.execute(sql, params=[
            c.email, c.password, c.name, c.field, c.num_employees, c.year_founded, c.website,
        ])


@router.get("/companies/{company_id}", response_model=CompanyRead, tags=["company"])
async def company_get(company_id: int):
    async with pool.connection() as conn, conn.cursor(row_factory=class_row(CompanyRead)) as cur:
        sql = "SELECT * FROM companies WHERE id = %s;"
        await cur.execute(sql, [company_id])
        record = await cur.fetchone()
        if record is None:
            raise HTTPException(404)
        return record


@router.put("/companies/{company_id}", tags=["company"])
async def company_patch(company_id: int, c: CompanyUpdate):
    async with pool.connection() as conn:
        sql = "UPDATE companies SET                                                 \
            email=%s, name=%s, field=%s, num_employees=%s, year_founded=%s, website=%s  \
            WHERE id=%s RETURNING *;"
        await conn.execute(sql, [c.email, c.name, c.field, c.num_employees, c.year_founded, c.website, company_id])


@router.delete("/companies/{company_id}", tags=["company"])
async def company_delete(company_id: int):
    async with pool.connection() as conn:
        sql = "DELETE FROM companies WHERE id = %s"
        await conn.execute(sql, [company_id])


""" Routes for OFFERS """

@router.post("/offers", status_code=status.HTTP_201_CREATED, tags=["offer"])
async def offer_post(o: OfferCreate):
    async with pool.connection() as conn:
        sql = "INSERT INTO offers                                                   \
            (salary, num_weeks, field, deadline, requirements, responsibilities)    \
            VALUES (%s, %s, %s, %s, %s, %s)"
        await conn.execute(sql, params=[
            o.salary, o.num_weeks, o.field, o.deadline, o.requirements, o.responsibilities
        ])


@router.get("/offers", response_model=list[OfferRead], tags=["offer"])
async def offers_get():
    async with pool.connection() as conn, conn.cursor(row_factory=class_row(OfferRead)) as cur:
        sql = "SELECT * FROM offers;"
        await cur.execute(sql)
        records = await cur.fetchall()
        return records


@router.get("/offers/{offer_id}", response_model=OfferRead, tags=["offer"])
async def offer_get(offer_id: int):
    async with pool.connection() as conn, conn.cursor(row_factory=class_row(OfferRead)) as cur:
        sql = "SELECT * FROM offers WHERE id = %s;"
        await cur.execute(sql, [offer_id])
        record = await cur.fetchone()
        if record is None:
            raise HTTPException(404)
        return record


@router.put("/offers/{offer_id}", tags=["offer"])
async def offer_patch(offer_id: int, s: OfferUpdate):
    async with pool.connection() as conn:
        sql = "UPDATE offers SET                                                                    \
            salary=%s, num_weeks=%s, field=%s, deadline=%s, requirements=%s, responsibilities=%s    \
            WHERE id=%s RETURNING *;"
        await conn.execute(sql, [s.salary, s.num_weeks, s.field, s.deadline, s.requirements, s.responsibilities, offer_id])
    

@router.delete("/offers/{offer_id}", tags=["offer"])
async def offer_delete(offer_id: int):
    async with pool.connection() as conn:
        sql = "DELETE FROM offers WHERE id = %s"
        await conn.execute(sql, [offer_id])



"""
class ToDo(BaseModel):
    id: int | None
    name: str
    completed: bool


@router.post("")
async def create_todo(todo: ToDo):
    async with pool.connection() as conn:
        await conn.execute(
            "insert into todos (name, completed) values (%s, %s)",
            [todo.name, todo.completed],
        )


@router.get("")
async def get_todos():
    async with pool.connection() as conn, conn.cursor(
        row_factory=class_row(ToDo)
    ) as cur:
        await cur.execute("select * from todos")
        records = await cur.fetchall()
        return records


@router.get("/{id}")
async def get_todo(id: int):
    async with pool.connection() as conn, conn.cursor(
        row_factory=class_row(ToDo)
    ) as cur:
        await cur.execute("select * from todos where id=%s", [id])
        record = await cur.fetchone()
        if not record:
            raise HTTPException(404)
        return record


@router.put("/{id}")
async def update_todo(id: int, todo: ToDo):
    async with pool.connection() as conn, conn.cursor(
        row_factory=class_row(ToDo)
    ) as cur:
        await cur.execute(
            "update todos set name=%s, completed=%s where id=%s returning *",
            [todo.name, todo.completed, id],
        )
        record = await cur.fetchone()
        return record


@router.delete("/{id}")
async def delete_todo(id: int):
    async with pool.connection() as conn:
        await conn.execute("delete from todos where id=%s", [id])
"""
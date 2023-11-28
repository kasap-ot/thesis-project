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

@router.post("/students", status_code=status.HTTP_201_CREATED)
async def student_post(s: StudentCreate):
    async with pool.connection() as conn:
        sql = "INSERT INTO students                                                 \
            (email, hashed_password, name, age, university, major, credits, gpa)    \
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        await conn.execute(sql, params=[
            s.email, s.password, s.name, s.age, s.university, s.major, s.credits, s.gpa,
        ])


@router.get("/students", response_model=list[StudentRead])
async def students_get():
    async with pool.connection() as conn, conn.cursor(row_factory=class_row(StudentRead)) as cur:
        sql = "SELECT * FROM students;"
        await cur.execute(sql)
        records = await cur.fetchall()
        return records


@router.get("/students/{student_id}", response_model=StudentRead)
async def student_get(student_id: int):
    async with pool.connection() as conn, conn.cursor(row_factory=class_row(StudentRead)) as cur:
        sql = "SELECT * FROM students WHERE id = %s;"
        await cur.execute(sql, [student_id])
        record = await cur.fetchone()
        if record is None:
            raise HTTPException(404)
        return record

# student update
@router.put("/students/{student_id}", response_model=StudentRead)
async def student_patch(student_id: int, s: StudentUpdate):
    async with pool.connection() as conn, conn.cursor(row_factory=class_row(StudentRead)) as cur:
        sql = "UPDATE students SET      \
                email = %s,             \
                name = %s,              \
                age = %s,               \
                university = %s,        \
                major = %s,             \
                credits = %s,           \
                gpa = %s                \
            WHERE id = %s RETURNING *;"
        await cur.execute(sql, [s.email, s.name, s.age, s.university, s.major, s.credits, s.gpa, student_id])
        record = await cur.fetchone()
        return record
    

@router.delete("/students/{student_id}")
async def student_delete(student_id: int):
    async with pool.connection() as conn:
        sql = "DELETE FROM students WHERE id = %s"
        await conn.execute(sql, [student_id])


# company create
# company read one
# company update
# company delete

# offer create
# offer read all
# offer read one
# offer update
# offer delete

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
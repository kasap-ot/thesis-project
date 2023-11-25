from .enums import UserType
from .security import (
    Token,
    login_for_token,
    get_current_user,
)
from .models import (StudentCreate, StudentRead, StudentUpdate, Student,
                    CompanyCreate, CompanyRead, CompanyUpdate, Company,)
from .database import get_session
from .controllers import (register_student, get_students, get_student, update_student, delete_student,
                         register_company, get_companies, get_company, update_company, delete_company)
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session


router = APIRouter()


""" Routes for STUDENTS """

@router.post("/students", response_model=StudentRead, status_code=status.HTTP_201_CREATED, tags=["student"])
async def student_create(student: StudentCreate, session: Session = Depends(get_session)):
    return register_student(student, session)


@router.get("/students", response_model=list[StudentRead], tags=["student"])
async def students_read(session: Session = Depends(get_session)):
    return get_students(session)


@router.get("/students/{student_id}", response_model=StudentRead, tags=["student"])
async def student_read(student_id: int, session: Session = Depends(get_session)):
    return get_student(student_id, session)


@router.patch("/students/{student_id}", response_model=StudentRead, tags=["student"])
async def student_update(
    student_id: int,
    student: StudentUpdate,
    session: Session = Depends(get_session),
    current_student: Student = Depends(get_current_user),
):
    return update_student(student_id, student, session, current_student)


@router.delete("/students/{student_id}", response_model=StudentRead, tags=["student"])
async def student_delete(
    student_id: int,
    session: Session = Depends(get_session),
    current_student: Student = Depends(get_current_user),
):
    return delete_student(student_id, session, current_student)


""" Route for security tokens """

@router.post("/token/{user_type}", response_model=Token)
async def login(
    user_type: str,
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    email = form_data.username
    password = form_data.password
    return login_for_token(email, password, session, user_type)


""" Routes for COMPANIES """


@router.post("/companies", response_model=CompanyRead, status_code=status.HTTP_201_CREATED, tags=["company"])
async def company_create(company: CompanyCreate, session: Session = Depends(get_session)):
    return register_company(company, session)


@router.get("/companies", response_model=list[CompanyRead], tags=["company"])
async def companies_read(session: Session = Depends(get_session)):
    return get_companies(session)


@router.get("/companies/{company_id}", response_model=CompanyRead, tags=["company"])
async def company_read(company_id: int, session: Session = Depends(get_session)):
    return get_company(company_id, session)


@router.patch("/companies/{company_id}", response_model=CompanyRead, tags=["company"])
async def company_update(
    company_id: int,
    company: CompanyUpdate,
    session: Session = Depends(get_session),
    current_company: Company = Depends(get_current_user),
):
    return update_company(company_id, company, session, current_company)


# @router.delete("/students/{student_id}", response_model=StudentRead)
# async def student_delete(
#     student_id: int,
#     session: Session = Depends(get_session),
#     current_student: Student = Depends(get_current_student),
# ):
#     return delete_student(student_id, session, current_student)


"""
@router.get("/", response_class=HTMLResponse)
async def welcome(request: Request):
    return templates.TemplateResponse("welcome.html", {"request": request})


# ------------------------------ USERS ------------------------------


@router.get("/register", response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.get("/log-in", response_class=HTMLResponse)
async def log_in(request: Request):
    return templates.TemplateResponse("log-in.html", {"request": request})


# ------------------------------ STUDENTS ------------------------------


@router.get("/register-student", response_class=HTMLResponse)
async def register_student_template(request: Request):
    return templates.TemplateResponse("register-student.html", {"request": request})


@router.post("/register-student")
async def register_student(request: Request) -> RedirectResponse:
    # TODO: write student registration logic
    return RedirectResponse(url="/home-students")


@router.get("/student-profile", response_class=HTMLResponse)
async def student_profile(request: Request):
    return templates.TemplateResponse("student-profile.html", {"request": request})


@router.get("/student-profile-edit", response_class=HTMLResponse)
async def student_profile_edit(request: Request):
    return templates.TemplateResponse("student-profile-edit.html", {"request": request})


@router.get("/home-students")
async def home_students(request: Request):
    return templates.TemplateResponse("student-home.html", {"request": request})


# ------------------------------ COMPANIES ------------------------------


@router.get("/register-company", response_class=HTMLResponse)
async def register_company(request: Request):
    return templates.TemplateResponse("register-company.html", {"request": request})


@router.get("/company-profile", response_class=HTMLResponse)
async def company_profile(request: Request):
    return templates.TemplateResponse("company-profile.html", {"request": request})


@router.get("/company-profile-edit", response_class=HTMLResponse)
async def company_profile_edit(request: Request):
    return templates.TemplateResponse("company-profile-edit.html", {"request": request})


@router.get("/home-companies")
async def home_companies(request: Request):
    return templates.TemplateResponse("company-home.html", {"request": request})


# ------------------------------ OFFERS ------------------------------


@router.get("/offers", response_class=HTMLResponse)
async def offers(request: Request):
    return templates.TemplateResponse("offers.html", {"request": request})


@router.get("/offer", response_class=HTMLResponse)
async def offer(request: Request):
    return templates.TemplateResponse("offer.html", {"request": request})


@router.get("/offer-edit", response_class=HTMLResponse)
async def offer_edit(request: Request):
    return templates.TemplateResponse("offer-edit.html", {"request": request})


# ------------------------------ APPLICATIONS ------------------------------


@router.get("/applications", response_class=HTMLResponse)
async def applications(request: Request):
    return templates.TemplateResponse("applications.html", {"request": request})


@router.get("/applicants", response_class=HTMLResponse)
async def applicants(request: Request):
    return templates.TemplateResponse(
        "applicants.html",
        {
            "request": request,
            "colors": ["danger", "danger", "warning", "success", "success", "success"],
        },
    )
"""

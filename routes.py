from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from security import login_for_token, get_current_user, Token
from schemas import User
from database import fake_db
from uuid import UUID


router = APIRouter()


@router.post("/register")
async def register(user: User):
    fake_db.update({user.id: user})
    return fake_db[user.id]


@router.get("/users")
async def users_read():
    return fake_db


@router.get("/users/{user_id}")
async def user_read(user_id: UUID):
    return fake_db[user_id]


@router.put("/users/{user_id}")
async def user_update(user_id: UUID, user: User):
    fake_db[user_id] = user
    return fake_db[user_id]


@router.delete("/users/{user_id}")
async def user_delete(user_id: UUID, current_user: User = Depends(get_current_user)):
    return fake_db.pop(user_id)


@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    return login_for_token(form_data)


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

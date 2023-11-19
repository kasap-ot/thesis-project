from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from security import (
    Token,
    login_for_token, 
    verify_token, 
    pwd_context
)
from schemas import UserCreate, UserInDB, UserRead, UserUpdate
from database import fake_db, get_user


router = APIRouter()


@router.post("/register")
async def register(user: UserCreate) -> UserRead:
    """
    Takes in the user information.
    Checks if the username already exists.
    Hashes the provided password.
    Stores the user info (with the hash) in the DB.
    """
    user_in_db = get_user(fake_db, user.username)
    if user_in_db is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists",
        )
    hashed_password = pwd_context.hash(user.password)
    user_to_insert = UserInDB(
        **user.model_dump(), 
        hashed_password=hashed_password,
    )
    fake_db.update({user.username: user_to_insert.model_dump()})
    return fake_db[user.username]


@router.get("/users")
async def users_read() -> dict[str, UserRead]:
    return fake_db


@router.get("/users/{username}")
async def user_read(username: str) -> UserRead:
    return fake_db[username]


@router.put("/users/{username}", dependencies=[Depends(verify_token)])
async def user_update(username: str, user: UserUpdate) -> UserRead:
    fake_db[username] = user
    return fake_db[username]


@router.delete("/users/{username}", dependencies=[Depends(verify_token)])
async def user_delete(username: str) -> UserRead:
    return fake_db.pop(username)


@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    return login_for_token(form_data.username, form_data.password)


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

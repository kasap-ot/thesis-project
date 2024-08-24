from .database import get_async_pool
from .controllers import (
    applicants_get_controller,
    application_accept_controller,
    application_cancel_controller,
    application_post_controller,
    applications_get_controller,
    experience_delete_controller,
    experience_patch_controller,
    experience_post_controller,
    offer_delete_controller,
    offer_put_controller,
    restart_database_controller,
    token_controller,
    student_post_controller,
    student_put_controller,
    student_delete_controller,
    student_profile_get_controller,
    company_post_controller,
    company_get_controller,
    company_offers_get_controller,
    company_patch_controller,
    company_delete_controller,
    offer_post_controller,
    offers_get_controller,
    offer_get_controller,
)
from .security import get_current_user, Token
from .schemas import (
    StudentCreate,
    StudentRead,
    StudentUpdate,
    CompanyCreate,
    CompanyUpdate,
    OfferCreate,
    OfferRead,
    OfferUpdate,
    ExperienceCreate,
    ExperienceUpdate,
    StudentProfileRead,
)
from fastapi import APIRouter, status, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse


router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/test")
async def test():
    return "This is a test."


""" Routes for TOKENS """


@router.post("/token", response_model=Token, tags=["security"])
async def token(user_type_param: str, form_data: OAuth2PasswordRequestForm = Depends()):
    return await token_controller(user_type_param, form_data)


""" Routes for STUDENTS """


@router.post("/students", status_code=status.HTTP_201_CREATED, tags=["students"])
async def student_post(s: StudentCreate):
    await student_post_controller(s)


@router.put("/students/{student_id}", tags=["students"])
async def student_put(
    student_id: int, s: StudentUpdate, 
    current_user = Depends(get_current_user),
):
    await student_put_controller(student_id, s, current_user)


@router.delete("/students/{student_id}", tags=["students"])
async def student_delete(student_id: int, current_user = Depends(get_current_user)):
    await student_delete_controller(student_id, current_user)


@router.get("/students/profile/{student_id}", response_model=StudentProfileRead, tags=["students"])
async def student_profile_get(request: Request, student_id: int, current_user = Depends(get_current_user)):
    student = await student_profile_get_controller(student_id)
    return templates.TemplateResponse(
        name = "student-profile.html",
        context = {"request": request, "student": student, "current_user": current_user},
    )


@router.get("/students-home", response_class=HTMLResponse, tags=["static-templates"])
async def students_home_get(request: Request, current_user = Depends(get_current_user)):
    return templates.TemplateResponse("student-home.html", {"request": request, "current_user": current_user})


@router.get("/students/profile/{student_id}/edit", response_class=HTMLResponse, tags=["students"])
async def student_profile_edit_get(
    request: Request, 
    student_id: int, 
    _ = Depends(get_current_user)
):
    student_profile = await student_profile_get_controller(student_id)
    return templates.TemplateResponse(
        name = "student-profile-edit.html", 
        context = {"request": request, "student_profile": student_profile}
    )


""" Routes for COMPANIES """


@router.post("/companies", status_code=status.HTTP_201_CREATED, tags=["companies"])
async def company_post(c: CompanyCreate):
    await company_post_controller(c)


@router.get("/companies/{company_id}", response_class=HTMLResponse, tags=["companies"])
async def company_get(request: Request, company_id: int, current_user = Depends(get_current_user)):
    company = await company_get_controller(company_id)
    return templates.TemplateResponse(
        "company-profile.html", 
        {"request":  request, "company": company, "current_user": current_user}
    )


@router.get(
    "/companies/{company_id}/offers", response_model=list[OfferRead], tags=["companies"]
)
async def company_offers_get(request: Request, company_id: int, current_user = Depends(get_current_user)):
    offers = await company_offers_get_controller(company_id)
    return templates.TemplateResponse(
       name = "offers.html",
       context = {"request": request, "offers": offers, "current_user": current_user}
    )


@router.get("/companies/{company_id}/edit", response_class=HTMLResponse, tags=["companies"])
async def company_edit_get(request: Request, company_id: int):
    company = await company_get_controller(company_id)
    return templates.TemplateResponse(
        "company-profile-edit.html", 
        {"request": request, "company": company}
    )


@router.put("/companies/{company_id}", tags=["companies"])
async def company_patch(company_id: int, c: CompanyUpdate, current_user = Depends(get_current_user)):
    await company_patch_controller(company_id, c, current_user)


@router.delete("/companies/{company_id}", tags=["companies"])
async def company_delete(company_id: int, current_user = Depends(get_current_user)):
    await company_delete_controller(company_id, current_user)


@router.get("/companies-home", response_class=HTMLResponse, tags=["static-templates"])
async def companies_home_get(request: Request, current_user = Depends(get_current_user)):
    return templates.TemplateResponse("company-home.html", {"request": request, "current_user": current_user})


""" Routes for OFFERS """


@router.get("/offers-create", response_class=HTMLResponse, tags=["offers"])
async def offer_create_get(request: Request):
    return templates.TemplateResponse("offer-create.html", {"request": request})


@router.post("/offers", status_code=status.HTTP_201_CREATED, tags=["offers"])
async def offer_post(o: OfferCreate, current_user = Depends(get_current_user)):
    """
    Create a new offer. Companies can create offers only for themselves.
    """
    await offer_post_controller(o, current_user)


@router.get("/offers", response_class=HTMLResponse, tags=["offers"])
async def offers_get(
    request: Request,
    field: str | None = None,
    min_num_weeks: int = 0,
    max_num_weeks: int = 100,
    min_salary: int = 0,
    max_salary: int = 10_000,
    current_user = Depends(get_current_user)
):
    """ 
    Returns all offers that satisfy the given query parameters 
    """
    offers = await offers_get_controller(
        field, 
        min_num_weeks, 
        max_num_weeks, 
        min_salary, 
        max_salary,
    )
    return templates.TemplateResponse(
        name = "offers.html", 
        context = {
            "request": request, 
            "offers": offers, 
            "current_user": current_user,
        },
    )


@router.get("/offers/{offer_id}", response_class=HTMLResponse, tags=["offers"])
async def offer_get(request: Request, offer_id: int, current_user = Depends(get_current_user)):
    """
    Get a given offer. Anyone can view the offer.
    """
    offer = await offer_get_controller(offer_id)
    return templates.TemplateResponse(
        "offer.html", 
        {"request": request, "offer": offer, "current_user": current_user}
    )


@router.get("/offers/{offer_id}/edit", response_class=HTMLResponse, tags=["offers"])
async def offer_edit_get(request: Request, offer_id: int):
    offer = await offer_get_controller(offer_id)
    return templates.TemplateResponse("offer-edit.html", {"request": request, "offer": offer})


@router.put("/offers/{offer_id}", tags=["offers"])
async def offer_put(offer_id: int, o: OfferUpdate, current_user = Depends(get_current_user)):
    """
    Update a given offer. Only offer-owners are authorized.
    """
    await offer_put_controller(offer_id, o, current_user)


@router.delete("/offers/{offer_id}", tags=["offers"])
async def offer_delete(offer_id: int, current_user = Depends(get_current_user)):
    """
    Delete a given offer. Only offer-owners are authorized.
    """
    await offer_delete_controller(offer_id, current_user)


""" Routes for EXPERIENCES """


@router.post("/experiences", status_code=status.HTTP_201_CREATED, tags=["experiences"])
async def experience_post(e: ExperienceCreate, current_user = Depends(get_current_user)):
    """ 
    Create a new experience item. Students can 
    only create experience items for themselves. 
    """
    await experience_post_controller(e, current_user)


@router.put("/experiences/{experience_id}", tags=["experiences"])
async def experience_patch(experience_id: int, s: ExperienceUpdate, current_user = Depends(get_current_user)):
    """
    Update a given experience item. Only student-owners of the experience are allowed.
    """
    await experience_patch_controller(experience_id, s, current_user)


@router.delete("/experiences/{experience_id}", tags=["experiences"])
async def experience_delete(experience_id: int, current_user = Depends(get_current_user)):
    """
    Delete a give experience item. Only student-owners of the experience are allowed.
    """
    await experience_delete_controller(experience_id, current_user)


""" Routes for APPLICATIONS """


@router.post("/applications/apply/{student_id}/{offer_id}", tags=["applications"])
async def application_post(student_id: int, offer_id: int, current_user = Depends(get_current_user)):
    """
    Add an application from the student for the given offer. Students 
    will be authorized to create applications for themselves only.
    """
    await application_post_controller(student_id, offer_id, current_user)


@router.get(
    "/applications/view/{student_id}",
    response_class=HTMLResponse,
    tags=["applications"],
)
async def applications_get(request: Request, student_id: int, current_user = Depends(get_current_user)):
    """
    Get all applications of a given student. Only the 
    student-owner can access his applications.
    """
    applications = await applications_get_controller(student_id, current_user)
    return templates.TemplateResponse(
        name = "applications.html", 
        context = {"request": request, "applications": applications}, 
        headers = {"Content-Type": "text/html"},
    )


@router.patch("/applications/accept/{student_id}/{offer_id}", tags=["applications"])
async def application_accept(student_id: int, offer_id: int, current_user = Depends(get_current_user)):
    """
    If a student has status - waiting for a given application,
    set his his status to - accepted. Change all other applications
    to status - rejected.
    """
    await application_accept_controller(student_id, offer_id, current_user)


@router.delete("/applications/cancel/{student_id}/{offer_id}", tags=["applications"])
async def application_cancel(student_id: int, offer_id: int, current_user = Depends(get_current_user)):
    """
    If a student is still waiting for his application, simply delete his application.
    If the student's application has been accepted, then delete his application and
    reset all other applications (for the same offer) to status - waiting.
    """
    await application_cancel_controller(student_id, offer_id, current_user)


@router.get("/applications/applicants/{offer_id}", tags=["applications"], response_model=list[StudentRead])
async def applicants_get(request: Request, offer_id: int, current_user = Depends(get_current_user)):
    """
    Get all student-applicants that have applied for the given offer.
    """
    students = await applicants_get_controller(offer_id, current_user)
    return templates.TemplateResponse(
        name = "applicants.html",
        context = {"request": request, "students": students},
        headers = {"Content-Type": "text/html"}
    )
    

""" Routes for STATIC TEMPLATES """


@router.get("/", response_class=HTMLResponse, tags=["static-templates"])
async def welcome_get(request: Request):
    return templates.TemplateResponse("welcome.html", {"request": request})


@router.get("/register", response_class=HTMLResponse, tags=["static-templates"])
async def register_get(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.get("/register-student", response_class=HTMLResponse, tags=["static-templates"])
async def register_student_get(request: Request):
    return templates.TemplateResponse("register-student.html", {"request": request})


@router.get("/register-company", response_class=HTMLResponse, tags=["static-templates"])
async def register_company_get(request: Request):
    return templates.TemplateResponse("register-company.html", {"request": request})


@router.get("/log-in", response_class=HTMLResponse, tags=["static-templates"])
async def log_in_get(request: Request):
    return templates.TemplateResponse("log-in.html", {"request": request})


""" Routes for reseting the database """
@router.delete("/restart-database", status_code=status.HTTP_200_OK)
async def restart_database():
    await restart_database_controller()


""" Routes for testing Cockroach DB connection """


@router.get("/cockroach-db/1", tags=["cockroach"])
async def cockroach_1():
    async with get_async_pool().connection() as conn:
        sql = "USE test_connection; INSERT INTO test_table (id, name, age) VALUES (16, 'John Doe', 34);"
        await conn.execute(sql)
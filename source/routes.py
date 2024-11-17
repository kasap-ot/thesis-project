from typing import Annotated, Optional
from source.notifications import (
    notify_company_applicants_change, 
    notify_student_application_status_change,
    notify_students_application_status_change, 
    send_email_profile_created,
)
from .controllers import (
    applicants_get_controller,
    application_accept_controller,
    application_cancel_controller,
    application_post_controller,
    applications_get_controller,
    company_profile_get_controller,
    company_report_delete_controller,
    company_report_get_controller,
    company_report_post_controller,
    company_report_put_controller,
    complete_offer_controller,
    experience_delete_controller,
    experience_patch_controller,
    experience_post_controller,
    motivational_letter_delete_controller,
    motivational_letter_post_controller,
    motivational_letter_put_controller,
    offer_delete_controller,
    offer_file_post_controller,
    offer_put_controller,
    profile_picture_delete_controller,
    profile_picture_post_controller,
    profile_picture_put_controller,
    start_offer_controller,
    student_report_get_controller,
    subject_delete_controller,
    subject_patch_controller,
    subject_post_controller,
    token_controller,
    student_post_controller,
    student_put_controller,
    student_delete_controller,
    student_profile_get_controller,
    company_post_controller,
    company_get_controller,
    company_offers_get_controller,
    company_put_controller,
    company_delete_controller,
    offer_post_controller,
    offers_get_controller,
    offer_get_controller,
    student_report_post_controller,
    student_report_put_controller,
    student_report_delete_controller,
)
from .security import get_current_user, Token
from .schemas import (
    CompanyReport,
    StudentCreate,
    StudentUpdate,
    CompanyCreate,
    CompanyUpdate,
    OfferCreate,
    OfferRead,
    OfferUpdate,
    ExperienceCreate,
    ExperienceUpdate,
    Subject,
    MotivationalLetter,
    StudentReport,
)
from .enums import MAX_CREDITS, MAX_GPA, MIN_CREDITS, MIN_GPA, Status, Environment
from fastapi import APIRouter, BackgroundTasks, File, Form, UploadFile, status, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from os import getenv


router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/test")
async def test():
    return {"message": "This is a test message."}


# Routes for TOKENS


@router.post("/token", response_model=Token)
async def token(user_type_param: str, form_data: OAuth2PasswordRequestForm = Depends()):
    return await token_controller(user_type_param, form_data)


# Routes for STUDENTS


@router.post("/students", status_code=status.HTTP_201_CREATED)
async def student_post(s: StudentCreate, background_tasks: BackgroundTasks):
    await student_post_controller(s)
    if getenv(Environment.TESTING) == Environment.TRUE:
        return
    background_tasks.add_task(send_email_profile_created, s.email, s.name)


@router.put("/students/{student_id}")
async def student_put(
    student_id: int, s: StudentUpdate, 
    current_user = Depends(get_current_user),
):
    await student_put_controller(student_id, s, current_user)


@router.delete("/students/{student_id}")
async def student_delete(student_id: int, current_user = Depends(get_current_user)):
    await student_delete_controller(student_id, current_user)


@router.get("/students/profile/{student_id}", response_class=HTMLResponse)
async def student_profile_get(request: Request, student_id: int, current_user = Depends(get_current_user)):
    student_profile = await student_profile_get_controller(student_id)
    return templates.TemplateResponse(
        name = "student-profile.html",
        context = {
            "request": request, 
            "student_profile": student_profile, 
            "current_user": current_user
        },
    )


@router.get("/students-home", response_class=HTMLResponse)
async def students_home_get(request: Request, current_user = Depends(get_current_user)):
    return templates.TemplateResponse("student-home.html", {"request": request, "current_user": current_user})


@router.get("/students/profile/{student_id}/edit", response_class=HTMLResponse)
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


# Routes for COMPANIES


@router.post("/companies", status_code=status.HTTP_201_CREATED)
async def company_post(c: CompanyCreate, background_tasks: BackgroundTasks):
    await company_post_controller(c)
    if getenv(Environment.TESTING) == Environment.TRUE:
        return
    background_tasks.add_task(send_email_profile_created, c.email, c.name)


@router.get("/companies/{company_id}", response_class=HTMLResponse)
async def company_get(request: Request, company_id: int, current_user = Depends(get_current_user)):
    company = await company_profile_get_controller(company_id)
    return templates.TemplateResponse(
        "company-profile.html", 
        {"request":  request, "company": company, "current_user": current_user}
    )


@router.get("/companies/{company_id}/offers", response_model=list[OfferRead])
async def company_offers_get(request: Request, company_id: int, current_user = Depends(get_current_user)):
    offers = await company_offers_get_controller(company_id)
    return templates.TemplateResponse(
       name = "offers.html",
       context = {"request": request, "offers": offers, "current_user": current_user}
    )


@router.get("/companies/{company_id}/edit", response_class=HTMLResponse)
async def company_edit_get(request: Request, company_id: int):
    company = await company_get_controller(company_id)
    return templates.TemplateResponse(
        "company-profile-edit.html", 
        {"request": request, "company": company}
    )


@router.put("/companies/{company_id}")
async def company_put(company_id: int, c: CompanyUpdate, current_user = Depends(get_current_user)):
    await company_put_controller(company_id, c, current_user)


@router.delete("/companies/{company_id}")
async def company_delete(company_id: int, current_user = Depends(get_current_user)):
    await company_delete_controller(company_id, current_user)


@router.get("/companies-home", response_class=HTMLResponse)
async def companies_home_get(request: Request, current_user = Depends(get_current_user)):
    return templates.TemplateResponse("company-home.html", {"request": request, "current_user": current_user})


# Routes for OFFERS


@router.get("/offers-create", response_class=HTMLResponse)
async def offer_create_get(request: Request):
    return templates.TemplateResponse("offer-create.html", {"request": request})


@router.post("/offers", status_code=status.HTTP_201_CREATED)
async def offer_post(offer: OfferCreate, current_user = Depends(get_current_user)):
    """
    Create a new offer via form fields. 
    Companies can create offers only for themselves.
    """
    await offer_post_controller(offer, current_user)


@router.post("/offers/file", status_code=status.HTTP_201_CREATED, tags=["testing"])
async def offer_file_post(
    offer_file_bytes: Annotated[bytes, File()], 
    company_id: Annotated[int, Form()],
    current_user = Depends(get_current_user),
):
    """
    Create a new offer via an uploaded file.
    Only companies can create offers - for themselves.
    """
    await offer_file_post_controller(offer_file_bytes, company_id, current_user)


@router.get("/offers", response_class=HTMLResponse)
async def offers_get(
    request: Request,
    field: str | None = None,
    min_num_weeks: int = 0,
    max_num_weeks: int = 1000,
    min_salary: int = 0,
    max_salary: int = 1_000_000_000,
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
        current_user,
    )
    return templates.TemplateResponse(
        name = "offers.html", 
        context = {
            "request": request, 
            "offers": offers, 
            "current_user": current_user,
        },
    )


@router.get("/offers/{offer_id}", response_class=HTMLResponse)
async def offer_get(request: Request, offer_id: int, current_user = Depends(get_current_user)):
    """
    Get a given offer. Anyone can view the offer.
    """
    offer = await offer_get_controller(offer_id)
    return templates.TemplateResponse(
        "offer.html", 
        {
            "request": request, 
            "offer": offer, 
            "current_user": current_user
        }
    )


@router.get("/offers/{offer_id}/edit", response_class=HTMLResponse)
async def offer_edit_get(request: Request, offer_id: int):
    offer = await offer_get_controller(offer_id)
    return templates.TemplateResponse("offer-edit.html", {"request": request, "offer": offer})


@router.put("/offers/{offer_id}")
async def offer_put(offer_id: int, o: OfferUpdate, current_user = Depends(get_current_user)):
    """
    Update a given offer. Only offer-owners are authorized.
    """
    await offer_put_controller(offer_id, o, current_user)


@router.delete("/offers/{offer_id}")
async def offer_delete(offer_id: int, current_user = Depends(get_current_user)):
    """
    Delete a given offer. Only offer-owners are authorized.
    """
    await offer_delete_controller(offer_id, current_user)


# Routes for EXPERIENCES


@router.post("/experiences", status_code=status.HTTP_201_CREATED)
async def experience_post(e: ExperienceCreate, current_user = Depends(get_current_user)):
    """ 
    Create a new experience item. Students can 
    only create experience items for themselves. 
    """
    await experience_post_controller(e, current_user)


@router.put("/experiences/{experience_id}")
async def experience_patch(experience_id: int, s: ExperienceUpdate, current_user = Depends(get_current_user)):
    """
    Update a given experience item. Only student-owners of the experience are allowed.
    """
    await experience_patch_controller(experience_id, s, current_user)


@router.delete("/experiences/{experience_id}")
async def experience_delete(experience_id: int, current_user = Depends(get_current_user)):
    """
    Delete a given experience item. Only student-owners of the experience are allowed.
    """
    await experience_delete_controller(experience_id, current_user)


# Routes for SUBJECTS


@router.post("/subjects", status_code=status.HTTP_201_CREATED)
async def subject_post(s: Subject, current_user = Depends(get_current_user)):
    """
    Create a new subject entry for the currently logged in student.
    """
    await subject_post_controller(s, current_user)


@router.put("/subjects/{student_id}/{name}")
async def subject_patch(student_id: int, name: str, subject: Subject, current_user = Depends(get_current_user)):
    """
    Update a given subject entry. Only student-owners of the experience are authorized.
    """
    await subject_patch_controller(student_id, name, subject, current_user)


@router.delete("/subjects/{student_id}/{name}")
async def subject_delete(student_id: int, name: str, current_user = Depends(get_current_user)):
    """
    Delete a subject entry. Only the student owner is authorized.
    """
    await subject_delete_controller(student_id, name, current_user)


# Routes for APPLICATIONS


@router.post("/applications/apply/{student_id}/{offer_id}")
async def application_post(
    student_id: int, 
    offer_id: int, 
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user)
):
    """
    Add an application from the student for the given offer. Students 
    will be authorized to create applications for themselves only.
    """
    await application_post_controller(student_id, offer_id, current_user)
    
    if getenv(Environment.TESTING) == Environment.TRUE:
        return
    
    is_new_applicant = True
    background_tasks.add_task(notify_company_applicants_change, offer_id, is_new_applicant)


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


@router.patch("/applications/accept/{student_id}/{offer_id}")
async def application_accept(
    student_id: int, 
    offer_id: int,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user)
):
    """
    If a student has status - waiting for a given application,
    set his his status to - accepted. Change all other applications
    to status - rejected.
    """
    results = await application_accept_controller(student_id, offer_id, current_user)

    if getenv(Environment.TESTING) == Environment.TRUE:
        return
    
    background_tasks.add_task(
        notify_student_application_status_change, 
        results["accepted_student_id"], 
        offer_id, 
        Status.ACCEPTED
    )
    
    background_tasks.add_task(
        notify_students_application_status_change,
        results["rejected_student_ids"],
        offer_id,
        Status.REJECTED,
    )


@router.delete("/applications/cancel/{student_id}/{offer_id}")
async def application_cancel(
    student_id: int, 
    offer_id: int,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user)
):
    """
    If a student is still waiting for his application, simply delete his application.
    If the student's application has been accepted, then delete his application and
    reset all other applications (for the same offer) to status - waiting.
    """
    updated_student_ids = await application_cancel_controller(student_id, offer_id, current_user)

    if getenv(Environment.TESTING) == Environment.TRUE:
        return
    
    is_new_applicant = False
    background_tasks.add_task(
        notify_company_applicants_change, 
        offer_id, 
        is_new_applicant
    )
    
    background_tasks.add_task(
        notify_students_application_status_change, 
        updated_student_ids,
        offer_id,
        Status.WAITING,
    )


@router.get("/applications/applicants/{offer_id}")
async def applicants_get(
    request: Request, 
    offer_id: int, 
    university: Optional[str] = None,
    min_gpa: float = MIN_GPA,
    max_gpa: float = MAX_GPA,
    min_credits: int = MIN_CREDITS,
    max_credits: int = MAX_CREDITS,
    subjects: Optional[str] = None,
    current_user = Depends(get_current_user)
):
    """
    Get all student-applicants that have applied for the given offer.
    Return a subset of applicants if filter parameters are provided.
    """
    students = await applicants_get_controller(
        offer_id, 
        university,
        min_gpa,
        max_gpa,
        min_credits,
        max_credits,
        subjects,
        current_user,
    )
    return templates.TemplateResponse(
        name = "applicants.html",
        context = {"request": request, "students": students, "offer_id": offer_id},
        headers = {"Content-Type": "text/html"}
    )


@router.patch("/applications/start-offer/{student_id}/{offer_id}")
async def start_offer(
    student_id: int, 
    offer_id: int, 
    current_user = Depends(get_current_user),
):
    await start_offer_controller(student_id, offer_id, current_user)


@router.patch("/applications/complete-offer/{student_id}/{offer_id}")
async def complete_offer(
    student_id: int, 
    offer_id: int, 
    current_user = Depends(get_current_user),
):
    await complete_offer_controller(student_id, offer_id, current_user)
    

# Routes for STATIC TEMPLATES


@router.get("/", response_class=HTMLResponse)
async def welcome_get(request: Request):
    return templates.TemplateResponse("welcome.html", {"request": request})


@router.get("/register", response_class=HTMLResponse)
async def register_get(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.get("/register-student", response_class=HTMLResponse)
async def register_student_get(request: Request):
    return templates.TemplateResponse("register-student.html", {"request": request})


@router.get("/register-company", response_class=HTMLResponse)
async def register_company_get(request: Request):
    return templates.TemplateResponse("register-company.html", {"request": request})


@router.get("/log-in", response_class=HTMLResponse)
async def log_in_get(request: Request):
    return templates.TemplateResponse("log-in.html", {"request": request})


# Routes for MOTIVATION LETTERS


@router.post("/students/motivational-letter", status_code=status.HTTP_201_CREATED)
async def motivational_letter_post(motivational_letter: MotivationalLetter, current_user = Depends(get_current_user)):
    await motivational_letter_post_controller(motivational_letter, current_user)


@router.put("/students/motivational-letter/{student_id}")
async def motivational_letter_put(motivational_letter: MotivationalLetter, current_user = Depends(get_current_user)):
    await motivational_letter_put_controller(motivational_letter, current_user)


@router.delete("/students/motivational-letter/{student_id}")
async def motivational_letter_delete(student_id: int, current_user = Depends(get_current_user)):
    await motivational_letter_delete_controller(student_id, current_user)


# Routes for STUDENT REPORTS


@router.post("/student-reports", status_code=status.HTTP_201_CREATED)
async def student_report_post(
    student_report: StudentReport, 
    current_user = Depends(get_current_user)
):
    await student_report_post_controller(student_report, current_user)


@router.put("/student-reports")
async def student_report_put(
    student_report: StudentReport, 
    current_user = Depends(get_current_user)
):
    await student_report_put_controller(student_report, current_user)


@router.delete("/student-reports/{student_id}/{offer_id}")
async def student_report_delete(
    student_id: int, 
    offer_id: int, 
    current_user = Depends(get_current_user)
):
    await student_report_delete_controller(student_id, offer_id, current_user)


@router.get("/student-reports/create")
async def student_report_create(request: Request):
    return templates.TemplateResponse(
        "student-report-form.html", 
        {"request": request, "is_create": True}
    )


@router.get("/student-reports/edit/{student_id}/{offer_id}")
async def student_report_edit(request: Request, student_id: int, offer_id: int):
    student_report = await student_report_get_controller(student_id, offer_id)
    return templates.TemplateResponse("student-report-form.html", {
        "request": request,
        "student_report": student_report,
        "is_create": False,
    })


@router.get("/student-reports/{student_id}/{offer_id}")
async def student_report_get(request: Request, student_id: int, offer_id: int, current_user = Depends(get_current_user)):
    student_report = await student_report_get_controller(student_id, offer_id)
    return templates.TemplateResponse("student-report.html", {
        "request": request,
        "student_report": student_report,
        "current_user": current_user,
    })


# Routes for COMPANY REPORTS


@router.post("/company-reports", status_code=status.HTTP_201_CREATED)
async def company_report_post(company_report: CompanyReport, current_user = Depends(get_current_user)):
    await company_report_post_controller(company_report, current_user)


@router.put("/company-reports", status_code=status.HTTP_201_CREATED)
async def company_report_put(company_report: CompanyReport, current_user = Depends(get_current_user)):
    await company_report_put_controller(company_report, current_user)


@router.delete("/company-reports/{student_id}/{offer_id}")
async def company_report_delete(student_id: int, offer_id: int, current_user = Depends(get_current_user)):
    await company_report_delete_controller(student_id, offer_id, current_user)


@router.get("/company-reports/{student_id}/{offer_id}")
async def company_report_get(student_id: int, offer_id: int, request: Request, current_user = Depends(get_current_user)):
    company_report = await company_report_get_controller(student_id, offer_id)
    return templates.TemplateResponse("company-report.html", {
        "request": request,
        "company_report": company_report,
        "current_user": current_user,
    })


@router.get("/company-reports/edit/{student_id}/{offer_id}")
async def company_report_edit_get(student_id: int, offer_id: int, request: Request):
    company_report = await company_report_get_controller(student_id, offer_id)
    return templates.TemplateResponse("company-report-form.html", {
        "request": request,
        "company_report": company_report,
    })


# Routes for IMAGES


@router.post("/profile-picture", status_code=status.HTTP_201_CREATED)
async def profile_picture_post(picture: UploadFile, current_user = Depends(get_current_user)):
    await profile_picture_post_controller(picture, current_user)


@router.put("/profile-picture")
async def profile_picture_put(picture: UploadFile, current_user = Depends(get_current_user)):
    await profile_picture_put_controller(picture, current_user)


@router.delete("/profile-picture")
async def profile_picture_delete(current_user = Depends(get_current_user)):
    await profile_picture_delete_controller(current_user)
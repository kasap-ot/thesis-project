from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory='templates')


@app.get('/welcome')
async def welcome(request: Request):
    return templates.TemplateResponse('welcome.html', {'request': request})


@app.get('/register')
async def register(request: Request):
    return templates.TemplateResponse('register.html', {'request': request})

@app.get('/register-student')
async def register_student(request: Request):
    # return templates.TemplateResponse('register-student.html', {'request': request})
    return 'register student'

@app.get('/register-company')
async def register_company(request: Request):
    # return templates.TemplateResponse('register-company.html', {'request': request})
    return 'register company'


@app.get('/log-in')
async def log_in():
    return 'log in'


@app.get('/home-students')
async def home_students():
    return 'home students'


@app.get('/home-companies')
async def home_companies():
    return 'home companies'


@app.get('/offers')
async def offers():
    return 'offers'


@app.get('/applications')
async def applications():
    return 'applications'


@app.get('/applicants')
async def applicants():
    return 'applicants'


@app.get('/student-profile')
async def student_profile():
    return 'student profile'


@app.get('/company-profile')
async def company_profile():
    return 'company profile'

# others?
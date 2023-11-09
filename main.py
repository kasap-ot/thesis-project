from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import random

app = FastAPI()
app.mount('/static', StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory='templates')

def random_color():
    colors = ['primary', 'secondary', 'success', 'danger', 'warning', 'info', 'light', 'dark']
    return random.choice(colors)

templates.env.filters['random_color'] = random_color


@app.get('/')
async def welcome(request: Request):
    return templates.TemplateResponse('welcome.html', {'request': request})


@app.get('/register')
async def register(request: Request):
    return templates.TemplateResponse('register.html', {'request': request})

@app.get('/register-student')
async def register_student(request: Request):
    return templates.TemplateResponse('register-student.html', {'request': request})

@app.get('/register-company')
async def register_company(request: Request):
    return templates.TemplateResponse('register-company.html', {'request': request})


@app.get('/log-in')
async def log_in(request: Request):
    return templates.TemplateResponse('log-in.html', {'request': request})


@app.get('/home-students')
async def home_students():
    return 'home students'


@app.get('/home-companies')
async def home_companies():
    return 'home companies'


@app.get('/offers')
async def offers(request: Request):
    return templates.TemplateResponse('offers.html', {'request': request})


@app.get('/offer')
async def offer(request: Request):
    return templates.TemplateResponse('offer.html', {'request': request})


@app.get('/applications')
async def applications(request: Request):
    return templates.TemplateResponse('applications.html', {'request': request})


@app.get('/applicants')
async def applicants(request: Request):
    return templates.TemplateResponse(
        'applicants.html', 
        {
            'request': request,
            'limit': 6,
            'colors': ['danger', 'danger', 'warning', 'success', 'success', 'success']
        }
    )


@app.get('/student-profile')
async def student_profile(request: Request):
    return templates.TemplateResponse('student-profile.html', {'request': request})


@app.get('/company-profile')
async def company_profile(request: Request):
    return templates.TemplateResponse('company-profile.html', {'request': request})

# others?
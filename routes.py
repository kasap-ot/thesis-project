from main import app, templates
from fastapi.responses import HTMLResponse
from fastapi import Request

@app.get('/', response_class=HTMLResponse)
async def welcome(request: Request):
    return templates.TemplateResponse('welcome.html', {'request': request})


@app.get('/register', response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse('register.html', {'request': request})

@app.get('/register-student', response_class=HTMLResponse)
async def register_student(request: Request):
    return templates.TemplateResponse('register-student.html', {'request': request})

@app.get('/register-company', response_class=HTMLResponse)
async def register_company(request: Request):
    return templates.TemplateResponse('register-company.html', {'request': request})


@app.get('/log-in', response_class=HTMLResponse)
async def log_in(request: Request):
    return templates.TemplateResponse('log-in.html', {'request': request})


@app.get('/home-students')
async def home_students():
    return 'home students'


@app.get('/home-companies')
async def home_companies():
    return 'home companies'


@app.get('/offers', response_class=HTMLResponse)
async def offers(request: Request):
    return templates.TemplateResponse('offers.html', {'request': request})


@app.get('/offer', response_class=HTMLResponse)
async def offer(request: Request):
    return templates.TemplateResponse('offer.html', {'request': request})


@app.get('/applications', response_class=HTMLResponse)
async def applications(request: Request):
    return templates.TemplateResponse('applications.html', {'request': request})


@app.get('/applicants', response_class=HTMLResponse)
async def applicants(request: Request):
    return templates.TemplateResponse(
        'applicants.html', 
        {
            'request': request,
            'colors': ['danger', 'danger', 'warning', 'success', 'success', 'success']
        }
    )


@app.get('/student-profile', response_class=HTMLResponse)
async def student_profile(request: Request):
    return templates.TemplateResponse('student-profile.html', {'request': request})


@app.get('/company-profile', response_class=HTMLResponse)
async def company_profile(request: Request):
    return templates.TemplateResponse('company-profile.html', {'request': request})

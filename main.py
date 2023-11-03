from fastapi import FastAPI

app = FastAPI()

@app.get('/')
async def func():
    return 'This is a test from Kasap.'
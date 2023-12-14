from .routes import router
from .database import get_async_pool
import asyncio
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

async_pool = get_async_pool()


async def check_async_connections():
    while True:
        await asyncio.sleep(600)
        print("check async connections")
        await async_pool.check()


@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(check_async_connections())
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(router)
app.mount("/static", StaticFiles(directory="static"), name="static")



# * Primary tasks
# TODO: complete company-user functionalities
# TODO: fix /applicants route - Internal Server Error

# * Secondary tasks
# TODO: change types input tags where necessary (e.g. from text to date)
# TODO: add profile photos for users (companies and students)
# TODO: expand application-views (to include offer-information)
# TODO: implement pagination for offers, applications, and applicants
# TODO: fix bug - error message on login screen
# TODO: implement session-storage wherever possible (to reduce queries to DB)

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

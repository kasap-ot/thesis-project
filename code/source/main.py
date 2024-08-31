import asyncio
from contextlib import asynccontextmanager
from .database import get_async_pool
from .routes import router
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles


async_pool = get_async_pool()


async def check_async_connections():
    while True:
        await asyncio.sleep(600)
        print("Checking async connections...")
        await async_pool.check() 


@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(check_async_connections())
    yield
    await async_pool.close()


app = FastAPI(lifespan=lifespan)
app.include_router(router)
app.mount("/static", StaticFiles(directory="static"), name="static")


# TODO: Add "region" logic for applications
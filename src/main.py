from typing import Optional
from psycopg_pool import AsyncConnectionPool
from .routes import router
from .config import get_async_pool
import asyncio
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager


async_pool: Optional[AsyncConnectionPool] = None


async def check_async_connections():
    if not async_pool:
        raise RuntimeError("Async pool is not initialized...")
    while True:
        await asyncio.sleep(600)
        print("check async connections")
        await async_pool.check() 


@asynccontextmanager
async def lifespan(app: FastAPI):
    global async_pool
    async_pool = get_async_pool()
    asyncio.create_task(check_async_connections())
    yield
    await async_pool.close()


app = FastAPI(lifespan=lifespan)
app.include_router(router)
app.mount("/static", StaticFiles(directory="static"), name="static")

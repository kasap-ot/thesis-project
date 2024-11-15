import asyncio
from .routes import router
from fastapi import FastAPI
from .database import async_pool, get_settings
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from psycopg_pool import AsyncConnectionPool
from dotenv import load_dotenv


async def check_async_connections(db_pool: AsyncConnectionPool):
    while True:
        await asyncio.sleep(600)
        await db_pool.check() 


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_pool = async_pool()
    load_dotenv()
    asyncio.create_task(check_async_connections(db_pool))
    yield
    await db_pool.close()
    get_settings.cache_clear()
    async_pool.cache_clear()


app = FastAPI(lifespan=lifespan)
app.include_router(router)
app.mount("/static", StaticFiles(directory="static"), name="static")
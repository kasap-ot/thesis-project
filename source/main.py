import asyncio as aio
from .routes import router
from fastapi import FastAPI
from .database import async_pool
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from psycopg_pool import AsyncConnectionPool
from dotenv import load_dotenv


async def check_async_connections(db_pool: AsyncConnectionPool):
    while True:
        await aio.sleep(600)
        await db_pool.check() 


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_dotenv()
    
    if aio.get_event_loop().is_running():
        aio.set_event_loop_policy(aio.WindowsSelectorEventLoopPolicy())
    
    db_pool = async_pool()
    aio.create_task(check_async_connections(db_pool))
    
    yield

    await db_pool.close()
    async_pool.cache_clear()


app = FastAPI(lifespan=lifespan)
app.include_router(router)
app.mount("/static", StaticFiles(directory="static"), name="static")
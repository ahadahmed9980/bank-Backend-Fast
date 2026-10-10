
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.routes.auth_route import router as auth_router
from app.database.mongodb import create_indexes


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_indexes()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)

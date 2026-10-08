from fastapi import FastAPI
from app.routes.auth_route import router as auth_router
from app.database.mongodb import create_indexes

app = FastAPI()
app.include_router(auth_router)
@app.on_event("startup")
async def startup():
    await create_indexes()
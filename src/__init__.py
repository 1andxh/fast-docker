from fastapi import FastAPI
from .tasks.routes import router

app = FastAPI()

app.include_router(router)

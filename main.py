from fastapi import FastAPI

from adapters.orm import start_mappers
from logger import logger
from resources.routes import api_router

app = FastAPI(
    title="Amazing Product Catalog API",
)

app.include_router(api_router)
start_mappers()


@app.on_event("startup")
def startup():
    logger.info("Application is starting up")

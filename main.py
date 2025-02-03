from app.api.v1.endpoints.quotes import router as quotes_router
from app.core.logging import configure_logging

from fastapi import FastAPI

configure_logging()
app = FastAPI(
    title="Course Bundle System",
    description="API for calculating course bundle quotes",
    version="1.0.0"
)

app.include_router(quotes_router, prefix="/api/v1")
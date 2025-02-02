from fastapi import APIRouter
from typing import List
from app.models.schemas import TeacherRequest, Quote
from app.core.config import load_provider_config
from app.services.matcher import get_provider_matches

router = APIRouter()

@router.post("/quotes", response_model=List[Quote])
async def calculate_quotes(request: TeacherRequest):
    provider_config = load_provider_config()
    return get_provider_matches(request.topics, provider_config)
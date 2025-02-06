from fastapi import APIRouter
from database.mongodb_connection import preprocess_reviews

user = APIRouter(prefix="/api/user")

@review.post("/review/preprocess/{site_name}")
async def preprocess_site_reviews(site_name: str):
    """
    특정 사이트(site_name)의 리뷰 데이터를 MongoDB에서 가져와 전처리하고, 다시 저장하는 API
    """
    result = preprocess_reviews(site_name)
    return result

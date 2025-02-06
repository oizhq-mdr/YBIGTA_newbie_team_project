
from fastapi import APIRouter, HTTPException
from database.mongodb_connection import mongo_db
import importlib
import logging

review = APIRouter(prefix="/api")

@review.post("/review/preprocess/{site_name}")
async def preprocess_reviews(site_name: str):
    """
    특정 사이트(site_name)의 리뷰 데이터를 MongoDB에서 가져와 전처리하고, 다시 저장하는 API
    """

    collection = mongo_db["crawling_data"]

    try:
        # 전처리 모듈 동적 불러오기
        preprocessor_module = importlib.import_module(f"app.review_analysis.preprocessing.{site_name}_processor")
        PreprocessorClass = getattr(preprocessor_module, "Preprocessor")
    except ModuleNotFoundError:
        logging.error(f"No preprocessor found for site: {site_name}")
        raise HTTPException(status_code=400, detail=f"No preprocessor found for site: {site_name}")
    
    processor = PreprocessorClass()

    # site_name에 해당하는 리뷰 가져오기
    reviews = collection.find({"site_name": site_name})
    
    processed_count = 0
    for review in reviews:
        if "review" in review:
            processed_text = processor.process(review["review"])  # 전처리 수행
            collection.update_one({"_id": review["_id"]}, {"$set": {"processed_review": processed_text}})
            processed_count += 1

    return {"message": f"{processed_count} reviews processed and updated for {site_name}"}


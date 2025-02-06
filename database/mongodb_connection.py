from pymongo import MongoClient
from dotenv import load_dotenv
import os
import importlib  
import logging

load_dotenv()

mongo_url = os.getenv("MONGO_URL")

mongo_client = MongoClient(mongo_url)

mongo_db = mongo_client.get_database()

def preprocess_reviews(site_name):
    """MongoDB에서 site_name 데이터를 가져와 전처리 후 다시 저장"""
    collection = mongo_db["crawling_data"]

    try:
        preprocessor_module = importlib.import_module(f"app.review_analysis.preprocessing.{site_name}_processor")
        PreprocessorClass = getattr(preprocessor_module, "Preprocessor")  
    except ModuleNotFoundError:
        logging.error(f"No preprocessor found for site: {site_name}")
        return {"error": f"No preprocessor found for site: {site_name}"}
    
    processor = PreprocessorClass()

    reviews = collection.find({"site_name": site_name})
    
    processed_count = 0
    for review in reviews:
        if "review" in review:
            processed_text = processor.process(review["review"])  # 전처리 수행
            collection.update_one({"_id": review["_id"]}, {"$set": {"processed_review": processed_text}})
            processed_count += 1

    return {"message": f"{processed_count} reviews processed and updated for {site_name}"}

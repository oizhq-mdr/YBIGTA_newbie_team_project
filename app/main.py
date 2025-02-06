# main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
import os

# 예시) user_router가 내부에서 dependencies.py 의존성들을 사용
from app.user.user_router import user
from app.review.review_router import review 
from app.config import PORT

from database.mysql_connection import engine, Base
from app.user.user_repository import UserORM 

Base.metadata.create_all(bind=engine)

app = FastAPI()

# 정적 파일 마운트
static_path = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_path), name="static")

# 사용자 라우터 등록
app.include_router(user)
app.include_router(review) 

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=True)

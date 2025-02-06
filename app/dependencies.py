# dependencies.py
from fastapi import Depends
from sqlalchemy.orm import Session

from database.mysql_connection import SessionLocal
from app.user.user_repository import UserRepository
from app.user.user_service import UserService

def get_db() -> Session:

    """
    요청이 들어올 때마다 SQLAlchemy 세션(Session)을 생성합니다.
    yield를 사용해서 세션을 반환한 후, 요청 처리가 끝나면 finally 블록에서 세션을 닫습니다.
    """

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    """
    get_db() 함수를 통해 생성된 DB 세션(db)을 받아 UserRepository의 생성자에 전달합니다.
    """
    return UserRepository(db)

def get_user_service(repo: UserRepository = Depends(get_user_repository)) -> UserService:
    """
    get_user_repository()를 통해 생성된 Repository 인스턴스를 UserService에 전달합니다.
    """
    return UserService(repo)

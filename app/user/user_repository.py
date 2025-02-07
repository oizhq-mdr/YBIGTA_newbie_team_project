import json

from typing import Dict, Optional

from app.user.user_schema import User as UserSchema
from app.config import USER_DATA

from sqlalchemy.orm import Session #type: ignore
#from app.user.user_model import User as UserORM  # ORM 모델

from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String #type: ignore
from sqlalchemy.orm import declarative_base
Base = declarative_base()

# ORM 모델 정의 (원래 model.py에 정의하던 내용)
class UserORM(Base):
    __tablename__ = "users"  # 과제 명세에 따라 'users' 테이블명 지정

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(100), nullable=False)








class UserRepository:
    def __init__(self, db: Session) -> None:
        """
        기존에는 JSON 파일을 로드/저장했으나,
        이제는 DB 세션을 이용해 MySQL 테이블에 접근.
        """
        self.db = db

    def get_user_by_email(self, email: str) -> Optional[UserSchema]:
        """
        MySQL DB에서 email로 사용자 정보를 조회한다.
        조회된 결과를 Pydantic User 스키마(UserSchema)로 변환해 반환.
        """
        user_orm = self.db.query(UserORM).filter(UserORM.email == email).first()
        if not user_orm:
            return None

        # ORM 객체 -> Pydantic 스키마 변환
        return UserSchema(
            email=user_orm.email,
            password=user_orm.password,
            username=user_orm.username
        )

    def save_user(self, user: UserSchema) -> UserSchema:
        """
        새 사용자(DB에 없었던 경우)를 추가하거나,
        기존 사용자를 업데이트(이미 있을 경우)할 수 있다.
        
        여기서는 단순히 '추가' 로직 예시를 작성.
        필요한 경우, 중복 체크나 예외처리를 서비스 계층에서 수행 가능.
        """
        # 1) Pydantic User -> ORM User 변환
        user_orm = UserORM(
            email=user.email,
            password=user.password,
            username=user.username
        )

        # 2) DB에 저장
        self.db.add(user_orm)
        self.db.commit()
        self.db.refresh(user_orm)

        # 3) ORM User -> Pydantic User 변환 후 반환
        return UserSchema(
            email=user_orm.email,
            password=user_orm.password,
            username=user_orm.username
        )

    def delete_user(self, user: UserSchema) -> Optional[UserSchema]:
        """
        Pydantic User 정보를 받아, DB에서 해당 사용자를 삭제한다.
        """
        user_orm = self.db.query(UserORM).filter(UserORM.email == user.email).first()
        if not user_orm:
            # 사용자를 찾을 수 없으면 None 반환 또는 예외 발생
            return None

        self.db.delete(user_orm)
        self.db.commit()
        return user  # 이미 Pydantic이므로 그대로 반환
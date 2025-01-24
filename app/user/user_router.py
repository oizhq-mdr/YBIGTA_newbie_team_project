from fastapi import APIRouter, HTTPException, Depends, status
from app.user.user_schema import User, UserLogin, UserUpdate, UserDeleteRequest
from app.user.user_service import UserService
from app.dependencies import get_user_service
from app.responses.base_response import BaseResponse

user = APIRouter(prefix="/api/user")


@user.post("/login", response_model=BaseResponse[User], status_code=status.HTTP_200_OK)
def login_user(user_login: UserLogin, service: UserService = Depends(get_user_service)) -> BaseResponse[User]:
    try:
        user = service.login(user_login)
        return BaseResponse(status="success", data=user, message="Login Success.")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@user.post("/register", response_model=BaseResponse[User], status_code=status.HTTP_201_CREATED)
def register_user(user: User, service: UserService = Depends(get_user_service)) -> BaseResponse[User]:
    """
    새 유저 등록 (회원가입) Endpoint
    
    Args:
        user: 회원가입 요청 데이터를 포함한 User 객체.
            - email (str): 유저 이메일
            - password (str): 유저 비밀번호
            - username (str): 유저 이름
        
        service: UserService 객체

    Raises:
        HTTPException(400): 이메일이 이미 등록된 경우

    Returns:
        BaseResponse[User]: 등록 성공 시 새 유저 정보와 메시지를 포함한 응답 객체 반환
    """
    try:
        user = service.register_user(user)
        return BaseResponse(status='success', data=user, message='User registration success.')
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@user.delete("/delete", response_model=BaseResponse[User], status_code=status.HTTP_200_OK)
def delete_user(user_delete_request: UserDeleteRequest, service: UserService = Depends(get_user_service)) -> BaseResponse[User]:
    """
    사용자를 시스템에서 삭제합니다

    Args:
        user_delete_request (UserDeleteRequest): 삭제할 사용자의 이메일이 포함된 요청
        service (UserService, optional): UserService 인스턴스

    Raises:
        HTTPException: 사용자를 찾을 수 없는 경우 404 에러 발생

    Returns:
        BaseResponse[User]: 삭제된 사용자 정보를 포함한 응답
    """
    try:
        deleted_user = service.delete_user(user_delete_request.email)
        return BaseResponse(status="success", data=deleted_user, message="User Deleted Successfully.")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@user.put("/update-password", response_model=BaseResponse[User], status_code=status.HTTP_200_OK)
def update_user_password(user_update: UserUpdate, service: UserService = Depends(get_user_service)) -> BaseResponse[User]:
    """
    사용자의 비밀번호를 업데이트합니다.

    Args:
        user_update (UserUpdate): 비밀번호 업데이트를 요청하는 사용자 정보와 새 비밀번호를 포함한 요청 객체
        service (UserService, optional): UserService 인스턴스로, 사용자 관련 비즈니스 로직을 처리

    Raises:
        HTTPException: 
            - 사용자를 찾을 수 없는 경우 404 에러 발생
            - 그 외 다른 오류 발생 시 400 에러 발생

    Returns:
        BaseResponse[User]: 비밀번호가 업데이트된 사용자 정보를 포함한 응답 객체
    """
    try:
        updated_user = service.update_user_pwd(user_update)
        return BaseResponse(status="success", data=updated_user, message="Password updated successfully.")
    except ValueError as e:

        if "User not Found." in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))

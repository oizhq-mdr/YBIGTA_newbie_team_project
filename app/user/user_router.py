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
@user.post("/register", response_model=BaseResponse[User], status_code=status.HTTP_201_CREATED)
def register_user(user: User, service: UserService = Depends(get_user_service)) -> BaseResponse[User]:
    '''
    새 유저 등록 (회원가입) Endpoint
    
    Args:
        user: 회원가입 요청 데이터를 포함한 User 객체.
            - email (str): 유저 이메일
            - password (str): 유저 비밀번호
            - username (str): 유저 이름
        
        service: UserService 객체

    Raises ValueError:
        HTTPException(400): 이메일이 이미 등록된 경우

    Returns:
        BaseResponse[User]: 등록 성공 시 새 유저 정보와 메시지를 포함한 응답 객체 반환
    '''

    try:
        user = service.register_user(user)
        return BaseResponse(status = 'success', data = user, message= ' User registeration success.')
    except ValueError as e:
        raise HTTPException(status_code= 400, detail = str(e))    ## TODO
    return None


@user.delete("/delete", response_model=BaseResponse[User], status_code=status.HTTP_200_OK)
def delete_user(user_delete_request: UserDeleteRequest, service: UserService = Depends(get_user_service)) -> BaseResponse[User]:
    ## TODO
    return None


@user.put("/update-password", response_model=BaseResponse[User], status_code=status.HTTP_200_OK)
def update_user_password(user_update: UserUpdate, service: UserService = Depends(get_user_service)) -> BaseResponse[User]:
    ## TODO
    return None

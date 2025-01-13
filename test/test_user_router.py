import pytest
import json
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch
from unittest.mock import MagicMock
from app.user.user_schema import User, UserLogin, UserUpdate, UserDeleteRequest
from app.responses.base_response import BaseResponse
from app.user.user_repository import UserRepository
from app.user.user_service import UserService
from app.dependencies import get_user_service
client = TestClient(app)

# Mock User 데이터
mock_user = User(email="test@example.com", password="password123", username="TestUser")

@pytest.fixture
def mock_user_service():
    with patch("app.user.user_service.UserService") as mock_service:
        yield mock_service

@pytest.fixture
def mock_user_repository():
    repo = MagicMock(spec=UserRepository)
    return repo

# 테스트: 회원가입 성공
def test_register_user_success(mock_user_repository):
    # UserService에 Mock Repository 주입
    service = UserService(userRepoitory=mock_user_repository)

    # 테스트 데이터
    new_user = User(email="unique@example.com", password="password123", username="TestUser")
    
    mock_user_repository.get_user_by_email.return_value = None  # 유저가 없는 상태
    mock_user_repository.save_user.return_value = new_user  # 저장된 유저 반환
    
    # 테스트 실행
    result = service.regiser_user(new_user)
    
    # 결과 검증
    assert result.email == "unique@example.com"
    assert result.username == "TestUser"
    mock_user_repository.get_user_by_email.assert_called_once_with("unique@example.com")
    mock_user_repository.save_user.assert_called_once_with(new_user)
    
# 테스트: 회원가입 실패 (이미 존재하는 유저)
def test_register_user_already_exists(mock_user_service):
    app.dependency_overrides[get_user_service] = lambda: mock_user_service.return_value

    mock_user_service.return_value.regiser_user.side_effect = ValueError("User already Exists.")

    response = client.post(
        "/api/user/register",
        json={"email": "test@example.com", "password": "password123", "username": "TestUser"}
    )

    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "User already Exists."

    # 의존성 초기화
    app.dependency_overrides = {}

# 테스트: 로그인 성공
def test_login_success(mock_user_service):
    mock_user_service.return_value.login.return_value = mock_user
    response = client.post("/api/user/login", json={"email": "new@example.com", "password": "password123"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["email"] == "new@example.com"
    assert data["data"]["username"] == "TestUser"

# 테스트: 로그인 실패 (유저 없음)
def test_login_user_not_found(mock_user_service):
    mock_user_service.return_value.login.side_effect = ValueError("User not found")
    response = client.post("/api/user/login", json={"email": "nonexistent@example.com", "password": "password123"})

    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "User not found"


# 테스트: 비밀번호 업데이트 성공
def test_update_password_success(mock_user_service):
    # 의존성 오버라이드 설정
    app.dependency_overrides[get_user_service] = lambda: mock_user_service.return_value

    updated_user = User(email="test@example.com", password="newpassword123", username="TestUser")
    mock_user_service.return_value.update_user_pwd.return_value = updated_user

    response = client.put(
        "/api/user/update-password",
        json={"email": "test@example.com", "new_password": "newpassword123"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["email"] == "test@example.com"
    assert data["data"]["password"] == "newpassword123"

    # 의존성 초기화
    app.dependency_overrides = {}

# 테스트: 비밀번호 업데이트 실패 (유저 없음)
def test_update_password_user_not_found(mock_user_service):
    mock_user_service.return_value.update_user_pwd.side_effect = ValueError("User not Found")
    response = client.put("/api/user/update-password", json={"email": "nonexistent@example.com", "new_password": "newpassword123"})

    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "User not Found"

def test_delete_user_success(mock_user_service):
    # FastAPI 의존성 오버라이드 설정
    app.dependency_overrides[get_user_service] = lambda: mock_user_service.return_value

    # Mock UserService 설정
    mock_user_service.return_value.delete_user.return_value = User(
        email="test@example.com",
        password="password123",
        username="TestUser"
    )

    # DELETE 요청
    response = client.request(
        "DELETE",
        "/api/user/delete",
        json={"email": "test@example.com"}  # 요청 본문 데이터
    )

    # 응답 검증
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["email"] == "test@example.com"

    # 의존성 초기화
    app.dependency_overrides = {}
    
@patch("app.user.user_service.UserService")
def test_delete_user_not_found(mock_user_service):
    mock_user_service.return_value.delete_user.side_effect = ValueError("User not Found.")
    response = client.request("DELETE", "/api/user/delete", json={"email": "nonexistent@example.com"})
    
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "User not Found."

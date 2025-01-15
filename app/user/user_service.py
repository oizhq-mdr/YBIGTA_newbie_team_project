    def login(self, user_login: UserLogin) -> User:
        '''
        로그인 처리 method
        
        Args: 
        
        user_login: UserLogin 객체
            - 따라서 user_login은 email과 password값을 가짐
            
        Raises ValueError:
            1. email이 등록되지 않은 경우
            2. email은 등록됐지만 비밀번호가 틀린 경우
        
        Return:
            로그인 성공 시 유저 정보를 포함한 user 반환
        '''
        user = self.repo.get_user_by_email(user_login.email)
        if not user:
            raise ValueError('User not Found.')
        
        if user.password != user_login.password:
            raise ValueError('Invalid ID/PW')
        
        return user
        
    def register_user(self, new_user: User) -> User:
        '''
        새 유저 등록 method
        
        Args:
            new_user: 새로 등록할 유저 데이터를 포함한 User 객체
                - 따라서 email, password, username 값을 가짐
            
        Raises ValueError:
            이메일이 이미 등록되어있는 경우
        
        오류 없을 시 save_user method로 새 user 정보를 json파일에 dumping
        
        Return:
            등록 성공 시 새 유저 정보를 포함한 user 반환
        '''
        if self.repo.get_user_by_email(new_user.email):
            raise ValueError('User already Exists.')
        
        new_user = self.repo.save_user(new_user)
        
        return new_userfrom app.user.user_repository import UserRepository
from app.user.user_schema import User, UserLogin, UserUpdate

class UserService:
    def __init__(self, userRepoitory: UserRepository) -> None:
        self.repo = userRepoitory

    def login(self, user_login: UserLogin) -> User:
        user = self.repo.get_user_by_email(user_login.email)
        if not user:
            raise ValueError("User not Found.")
        if user.password != user_login.password:
            raise ValueError("Invalid ID/PW")
        return user
        
    def register_user(self, new_user: User) -> User:
        ## TODO
        new_user = None
        return new_user

    def delete_user(self, email: str) -> User:
        ## TODO        
        deleted_user = None
        return deleted_user

    def update_user_pwd(self, user_update: UserUpdate) -> User:
        ## TODO
        updated_user = None
        return updated_user
        

from app.user.user_repository import UserRepository
from app.user.user_schema import User, UserLogin, UserUpdate


class UserService:
    def __init__(self, userRepoitory: UserRepository) -> None:
        self.repo = userRepoitory

    def login(self, user_login: UserLogin) -> User:
        """
        로그인 처리 메서드

        Args:
            user_login (UserLogin): 로그인 요청 데이터를 포함한 객체
                - email (str): 유저 이메일
                - password (str): 유저 비밀번호

        Raises:
            ValueError: 이메일이 등록되지 않았거나 비밀번호가 일치하지 않을 경우 발생

        Returns:
            User: 로그인 성공 시 반환되는 사용자 정보
        """
        user = self.repo.get_user_by_email(user_login.email)
        if not user:
            raise ValueError("User not Found.")
        if user.password != user_login.password:
            raise ValueError("Invalid ID/PW")
        return user

    def register_user(self, new_user: User) -> User:
        """
        새 유저 등록 메서드

        Args:
            new_user (User): 새로 등록할 사용자 데이터를 포함한 객체
                - email (str): 유저 이메일
                - password (str): 유저 비밀번호
                - username (str): 유저 이름

        Raises:
            ValueError: 이메일이 이미 등록된 경우 발생

        Returns:
            User: 등록된 사용자 정보
        """
        if self.repo.get_user_by_email(new_user.email):
            raise ValueError("User already Exists.")

        new_user = self.repo.save_user(new_user)
        return new_user

    def delete_user(self, email: str) -> User:
        """
        이메일로 사용자를 삭제합니다.

        Args:
            email (str): 삭제할 사용자의 이메일

        Raises:
            ValueError: 사용자를 찾을 수 없는 경우 에러 발생

        Returns:
            User: 삭제된 사용자 정보
        """
        user = self.repo.get_user_by_email(email)
        if not user:
            raise ValueError("User not Found.")
        return self.repo.delete_user(user)

    def update_user_pwd(self, user_update: UserUpdate) -> User:
        """
        사용자 비밀번호를 업데이트합니다.

        Args:
            user_update (UserUpdate): 업데이트 요청 데이터를 포함한 객체
                - email (str): 유저 이메일
                - new_password (str): 새 비밀번호

        Raises:
            ValueError: 사용자를 찾을 수 없는 경우 발생

        Returns:
            User: 업데이트된 사용자 정보
        """
        user = self.repo.get_user_by_email(user_update.email)
        if not user:
            raise ValueError("User not Found.")
        user.password = user_update.new_password
        return self.repo.save_user(user)

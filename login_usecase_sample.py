from src.infrastructure.db.repository.sqlalchemy_user_repository import SQLAlchemyUserRepository
from src.infrastructure.security.pw_hasher import BcryptPasswordHasher
from src.schemas.dto.auth import LoginDTO
from src.infrastructure.security.token_service import TokenService


class LoginUseCase:
    def __init__(self, user_repo: SQLAlchemyUserRepository, token_repo: TokenService):
        self.user_repo = user_repo
        self.token_repo = token_repo

    async def execute(self, login_dto: LoginDTO, pw_hasher: BcryptPasswordHasher):
        # get hashed pw from db.
        db_user = await self.user_repo.get_by_id(login_dto.id)
        if db_user is None:
            raise ValueError("User not found")
        result = pw_hasher.verify_password(login_dto.pw, db_user.pw_hashed)
        if not result:
            raise ValueError("Wrong password.")
        return self.token_repo.create_access_token(login_dto)

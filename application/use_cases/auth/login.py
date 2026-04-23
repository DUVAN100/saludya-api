from app.application.dtos.auth_dto import LoginDTO, TokenDTO
from app.application.ports.output.i_user_repository import IUserRepository
from app.domain.exceptions.domain_exceptions import (
    InvalidCredentialsException,
    InactiveUserException,
)


class LoginUseCase:
    """
    Caso de uso: autenticar un usuario y devolver un JWT.

    Delega en:
      - IUserRepository   → buscar el usuario por email
      - password_hasher   → verificar la contraseña
      - token_service     → generar el access token
    """

    def __init__(
        self,
        user_repository: IUserRepository,
        password_hasher,      # .verify(plain, hashed) -> bool
        token_service,        # .create_access_token(payload) -> str
    ) -> None:
        self._user_repo = user_repository
        self._hasher = password_hasher
        self._token_service = token_service

    async def execute(self, dto: LoginDTO) -> TokenDTO:
        # 1. Buscar usuario
        user = await self._user_repo.find_by_email(dto.email)
        print("user ", user)
        if not user:
            raise InvalidCredentialsException()
        print("="*60)
        print("DEBUG LOGIN:")
        print(f"Email: {dto.email}")
        print(f"Password recibido (longitud): {len(dto.password)}")
        print(f"Hash guardado en BD : {user.password_hash}")
        print(f"Hash empieza con   : {user.password_hash[:30]}...")
        
        # Verificación
        is_valid = self._hasher.verify(dto.password, user.password_hash)
        
        print(f"¿Contraseña válida? → {is_valid}")
        # 2. Verificar contraseña
        if not self._hasher.verify(dto.password, user.password_hash):
            raise InvalidCredentialsException()

        # 3. Verificar que la cuenta esté activa
        if not user.is_active:
            raise InactiveUserException()

        # 4. Generar token
        token = self._token_service.create_access_token(
            payload={"sub": str(user.id), "role": user.role.value}
        )
        print("token ", token)

        return TokenDTO(access_token=token)
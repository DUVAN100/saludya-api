from abc import ABC, abstractmethod

from app.application.dtos.auth_dto import LoginDTO, TokenDTO, TokenPayloadDTO


class IAuthService(ABC):
    """
    Puerto de entrada — interfaz que expone las operaciones
    de autenticación hacia los adaptadores de entrada.
    """

    @abstractmethod
    async def login(self, dto: LoginDTO) -> TokenDTO:
        ...

    @abstractmethod
    def decode_token(self, token: str) -> TokenPayloadDTO:
        ...
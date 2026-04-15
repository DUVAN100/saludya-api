from passlib.context import CryptContext


class PasswordHasher:
    """
    Adaptador de seguridad — hashea y verifica contraseñas con bcrypt.
    bcrypt incluye el salt automáticamente en el hash resultante.
    """

    def __init__(self) -> None:
        self._context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash(self, plain_password: str) -> str:
        """Retorna el hash bcrypt de la contraseña en texto plano."""
        return self._context.hash(plain_password)

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        """Retorna True si la contraseña coincide con el hash."""
        return self._context.verify(plain_password, hashed_password)
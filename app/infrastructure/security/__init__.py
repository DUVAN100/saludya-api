__all__ = ["PasswordHasher", "JWTHandler"]


def __getattr__(name: str):
    if name == "PasswordHasher":
        from .password_hasher import PasswordHasher

        return PasswordHasher
    if name == "JWTHandler":
        from .jwt_handler import JWTHandler

        return JWTHandler
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

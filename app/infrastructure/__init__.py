__all__ = [
    "Settings",
    "get_settings",
    "settings",
    "PasswordHasher",
    "JWTHandler",
    "Base",
    "engine",
    "AsyncSessionFactory",
    "get_db_session",
    "UserModel",
    "PatientModel",
    "DoctorModel",
    "DoctorAvailabilityModel",
    "AppointmentModel",
]


def __getattr__(name: str):
    if name in {"Settings", "get_settings", "settings"}:
        from .config import Settings, get_settings, settings

        return {"Settings": Settings, "get_settings": get_settings, "settings": settings}[name]

    if name in {"PasswordHasher", "JWTHandler"}:
        from .security import JWTHandler, PasswordHasher

        return {"PasswordHasher": PasswordHasher, "JWTHandler": JWTHandler}[name]

    if name in {
        "Base",
        "engine",
        "AsyncSessionFactory",
        "get_db_session",
        "UserModel",
        "PatientModel",
        "DoctorModel",
        "DoctorAvailabilityModel",
        "AppointmentModel",
    }:
        from .persistence import (
            AppointmentModel,
            AsyncSessionFactory,
            Base,
            DoctorAvailabilityModel,
            DoctorModel,
            PatientModel,
            UserModel,
            engine,
            get_db_session,
        )

        return {
            "Base": Base,
            "engine": engine,
            "AsyncSessionFactory": AsyncSessionFactory,
            "get_db_session": get_db_session,
            "UserModel": UserModel,
            "PatientModel": PatientModel,
            "DoctorModel": DoctorModel,
            "DoctorAvailabilityModel": DoctorAvailabilityModel,
            "AppointmentModel": AppointmentModel,
        }[name]

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

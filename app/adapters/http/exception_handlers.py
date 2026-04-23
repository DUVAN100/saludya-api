from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.domain.exceptions.domain_exceptions import (
    DomainException,
    UserNotFoundException,
    UserAlreadyExistsException,
    InvalidCredentialsException,
    InactiveUserException,
    PatientNotFoundException,
    PatientAlreadyExistsException,
    DoctorNotFoundException,
    DoctorNotAvailableException,
    AppointmentNotFoundException,
    AppointmentSlotTakenException,
    InvalidStatusTransitionException,
    AppointmentOutsideWorkingHoursException,
    AppointmentInThePastException,
)


def register_exception_handlers(app: FastAPI) -> None:
    """
    Registra handlers que mapean cada excepción de dominio
    al código HTTP correcto — sin try/except en los routes.
    """

    @app.exception_handler(UserNotFoundException)
    @app.exception_handler(PatientNotFoundException)
    @app.exception_handler(DoctorNotFoundException)
    @app.exception_handler(AppointmentNotFoundException)
    async def not_found_handler(request: Request, exc: DomainException):
        return JSONResponse(status_code=404, content={"detail": exc.message})

    @app.exception_handler(UserAlreadyExistsException)
    @app.exception_handler(PatientAlreadyExistsException)
    @app.exception_handler(AppointmentSlotTakenException)
    async def conflict_handler(request: Request, exc: DomainException):
        return JSONResponse(status_code=409, content={"detail": exc.message})

    @app.exception_handler(InvalidCredentialsException)
    @app.exception_handler(InactiveUserException)
    async def unauthorized_handler(request: Request, exc: DomainException):
        return JSONResponse(status_code=401, content={"detail": exc.message})

    @app.exception_handler(DoctorNotAvailableException)
    @app.exception_handler(InvalidStatusTransitionException)
    @app.exception_handler(AppointmentOutsideWorkingHoursException)
    @app.exception_handler(AppointmentInThePastException)
    async def unprocessable_handler(request: Request, exc: DomainException):
        return JSONResponse(status_code=422, content={"detail": exc.message})
"""
RitaDrishti-AI — Custom Exceptions and Centralized Structured Error Handling
"""

from fastapi import Request
from fastapi.responses import JSONResponse


class RitaDrishtiException(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400, retryable: bool = False):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.retryable = retryable


class ServiceUnavailableError(RitaDrishtiException):
    def __init__(self, code: str, message: str, retryable: bool = True, status_code: int = 503):
        super().__init__(code=code, message=message, status_code=status_code, retryable=retryable)


class AuthenticationError(RitaDrishtiException):
    def __init__(self, message: str = "Invalid credentials or token", code: str = "AUTHENTICATION_FAILED"):
        super().__init__(code=code, message=message, status_code=401, retryable=False)


class EntityNotFoundError(RitaDrishtiException):
    def __init__(self, message: str = "Entity not found", code: str = "ENTITY_NOT_FOUND"):
        super().__init__(code=code, message=message, status_code=404, retryable=False)


async def ritadrishti_exception_handler(request: Request, exc: RitaDrishtiException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "retryable": exc.retryable
            }
        }
    )

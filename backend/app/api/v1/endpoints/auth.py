"""
RitaDrishti-AI — Authentication API Endpoints
Public rate-limited endpoints for user registration and JWT authentication.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.core.security import create_access_token, verify_password
from backend.app.core.exceptions import AuthenticationError, EntityNotFoundError
from backend.app.core.rate_limiter import auth_rate_limiter
from backend.app.db.repositories import UserRepository
from backend.app.db.schemas import UserRegisterRequest, UserLoginRequest, TokenResponse, UserResponse

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(auth_rate_limiter)]
)
async def register_user(
    req: UserRegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Registers a new user account.
    Public, rate-limited endpoint.
    """
    user_repo = UserRepository(db)
    
    # Check if username or email already exists
    existing_user = await user_repo.get_user_by_username(req.username)
    if existing_user:
        raise AuthenticationError("Username already registered.")

    existing_email = await user_repo.get_user_by_email(req.email)
    if existing_email:
        raise AuthenticationError("Email address already registered.")

    user = await user_repo.create_user(
        email=req.email,
        username=req.username,
        password=req.password,
        full_name=req.full_name
    )
    return user


@router.post(
    "/login",
    response_model=TokenResponse,
    dependencies=[Depends(auth_rate_limiter)]
)
async def login_user(
    req: UserLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticates user and returns a Bearer JWT access token.
    Public, rate-limited endpoint.
    """
    user_repo = UserRepository(db)
    user = await user_repo.get_user_by_username(req.username)
    if not user:
        raise AuthenticationError("Invalid username or password.")

    if not verify_password(req.password, user.hashed_password):
        raise AuthenticationError("Invalid username or password.")

    if not user.is_active:
        raise AuthenticationError("User account is inactive.")

    token = create_access_token(subject=str(user.user_id))
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.user_id,
        "username": user.username
    }

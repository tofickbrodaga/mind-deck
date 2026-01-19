from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID

from infrastructure.database.database import get_db
from infrastructure.repositories.user_repository import UserRepository
from domain.entities.user import User
from presentation.schemas.user_schemas import UserCreate, UserResponse, UserLogin, TokenResponse
from infrastructure.security import verify_password, get_password_hash, create_access_token, decode_token

router = APIRouter()

security = HTTPBearer()


async def get_current_user_dependency(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Dependency для получения текущего пользователя из JWT токена"""
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception
    
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(UUID(user_id))
    if user is None:
        raise credentials_exception
    
    return user


async def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    user_repo: UserRepository = Depends(get_user_repository),
):
    """Регистрация нового пользователя"""
    # Проверяем, существует ли пользователь
    existing_user = await user_repo.get_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Создаем нового пользователя
    hashed_password = get_password_hash(user_data.password)
    user = User.create(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
    )
    
    created_user = await user_repo.create(user)
    return UserResponse(
        id=created_user.id,
        email=created_user.email,
        username=created_user.username,
        is_active=created_user.is_active,
        created_at=created_user.created_at,
        updated_at=created_user.updated_at,
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    user_repo: UserRepository = Depends(get_user_repository),
):
    """Вход в систему"""
    user = await user_repo.get_by_email(credentials.email)
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    return TokenResponse(access_token=access_token)


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    current_user: User = Depends(get_current_user_dependency),
):
    """Получить информацию о текущем пользователе"""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
    )

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm
)

from jose import JWTError, jwt
from passlib.context import CryptContext

from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.schemas.auth import (
    RegisterRequest,
    UserResponse
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# ============================================================
# PASSWORD HASHING
# ============================================================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(password: str) -> str:

    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    password_hash: str
) -> bool:

    return pwd_context.verify(
        plain_password,
        password_hash
    )


# ============================================================
# OAUTH2
# ============================================================

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


# ============================================================
# JWT
# ============================================================

def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None
):

    to_encode = data.copy()

    if expires_delta:

        expire = (
            datetime.now(timezone.utc)
            + expires_delta
        )

    else:

        expire = (
            datetime.now(timezone.utc)
            + timedelta(
                minutes=settings.access_token_expire_minutes
            )
        )

    to_encode["exp"] = expire

    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )

    return encoded_jwt


# ============================================================
# CURRENT USER
# ============================================================

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={
            "WWW-Authenticate": "Bearer"
        }
    )

    try:

        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        user_id = int(user_id)

    except (JWTError, ValueError):

        raise credentials_exception

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if user is None:
        raise credentials_exception

    return user


# ============================================================
# ROLE AUTHORIZATION
# ============================================================

def require_role(*allowed_roles: str):

    def role_checker(
        current_user: User = Depends(get_current_user)
    ):

        if current_user.role not in allowed_roles:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "You do not have permission "
                    "to access this resource"
                )
            )

        return current_user

    return role_checker


# ============================================================
# REGISTER
# ============================================================

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register_user(
    user_data: RegisterRequest,
    db: Session = Depends(get_db)
):

    existing_user = (
        db.query(User)
        .filter(
            User.email == user_data.email
        )
        .first()
    )

    if existing_user:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    hashed_password = hash_password(
        user_data.password
    )

    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hashed_password,
        role=user_data.role,
        organization=user_data.organization,
        is_verified=False
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# ============================================================
# LOGIN
# ============================================================

@router.post("/login")
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    user = (
        db.query(User)
        .filter(
            User.email == form_data.username
        )
        .first()
    )

    if not user:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    if not verify_password(
        form_data.password,
        user.password_hash
    ):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "role": user.role
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# ============================================================
# CURRENT USER
# ============================================================

@router.get(
    "/me",
    response_model=UserResponse
)
def get_me(
    current_user: User = Depends(get_current_user)
):

    return current_user


# ============================================================
# PROTECTED
# ============================================================

@router.get("/protected")
def protected_route(
    current_user: User = Depends(get_current_user)
):

    return {
        "message": "You are authenticated",
        "user_id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role,
        "organization": current_user.organization
    }


# ============================================================
# GOVERNMENT
# ============================================================

@router.get("/government-only")
def government_only(
    current_user: User = Depends(
        require_role("GOVERNMENT")
    )
):

    return {
        "message": "Government access granted",
        "user": current_user.name,
        "role": current_user.role
    }


# ============================================================
# HEALTH WORKER
# ============================================================

@router.get("/health-worker-only")
def health_worker_only(
    current_user: User = Depends(
        require_role("HEALTH_WORKER")
    )
):

    return {
        "message": "Health worker access granted",
        "user": current_user.name,
        "role": current_user.role
    }


# ============================================================
# FIELD WORKER
# ============================================================

@router.get("/field-worker-only")
def field_worker_only(
    current_user: User = Depends(
        require_role("FIELD_WORKER")
    )
):

    return {
        "message": "Field worker access granted",
        "user": current_user.name,
        "role": current_user.role
    }


# ============================================================
# LOGOUT
# ============================================================

@router.post("/logout")
def logout_user(
    current_user: User = Depends(get_current_user)
):

    return {
        "message": "Logout successful"
    }
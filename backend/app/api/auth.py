"""
EstateAI Authentication API Endpoints
Simple JWT-based auth with SQLite storage.
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta

from app.database import get_connection
from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from app.schemas.schemas import UserCreate, UserLogin, Token

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)


def create_access_token(data: dict):
    """Create a JWT token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify and decode JWT token."""
    if not credentials:
        return None
    try:
        payload = jwt.decode(
            credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM]
        )
        return payload
    except JWTError:
        return None


@router.post("/signup", response_model=Token)
def signup(user: UserCreate):
    """Register a new user."""
    conn = get_connection()

    # Check existing user
    existing = conn.execute(
        "SELECT id FROM users WHERE username = ? OR email = ?",
        (user.username, user.email),
    ).fetchone()

    if existing:
        conn.close()
        raise HTTPException(status_code=400, detail="Username or email already exists")

    hashed = pwd_context.hash(user.password)
    conn.execute(
        "INSERT INTO users (username, email, hashed_password) VALUES (?, ?, ?)",
        (user.username, user.email, hashed),
    )
    conn.commit()
    conn.close()

    token = create_access_token({"sub": user.username})
    return Token(access_token=token, username=user.username)


@router.post("/login", response_model=Token)
def login(user: UserLogin):
    """Authenticate user and return token."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE username = ?", (user.username,)
    ).fetchone()
    conn.close()

    if not row or not pwd_context.verify(user.password, row["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user.username})
    return Token(access_token=token, username=user.username)


@router.get("/me")
def get_current_user(payload: dict = Depends(verify_token)):
    """Get current authenticated user info."""
    if not payload:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {"username": payload.get("sub")}

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from datetime import timedelta
import uuid

from ....core.config import settings
from ....core.security import verify_password, get_password_hash, create_access_token
from ....db.base import query_db
from ....models.schemas import UserCreate, User, Token, TokenData

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    users = query_db(f"SELECT * FROM users WHERE email = '{token_data.email}'")
    if not users:
        raise credentials_exception
    return users[0]

@router.post("/register", response_model=User)
def register(user_in: UserCreate):
    existing_user = query_db(f"SELECT * FROM users WHERE email = '{user_in.email}'")
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    
    user_id = str(uuid.uuid4())
    hashed_password = get_password_hash(user_in.password)
    query_db(f"INSERT INTO users (id, email, password_hash) VALUES ('{user_id}', '{user_in.email}', '{hashed_password}')")
    
    user = query_db(f"SELECT * FROM users WHERE id = '{user_id}'")[0]
    return user

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    users = query_db(f"SELECT * FROM users WHERE email = '{form_data.username}'")
    if not users or not verify_password(form_data.password, users[0]["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=users[0]["email"], expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=User)
def read_user_me(current_user: dict = Depends(get_current_user)):
    return current_user

from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import models
from database import get_db

# Security configuration
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        role: str = payload.get("role")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return {"user_id": int(user_id), "role": role}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(token_data: dict = Depends(verify_token), db: Session = Depends(get_db)):
    user_id = token_data["user_id"]
    role = token_data["role"]
    
    if role == "employee":
        user = db.query(models.Employee).filter(models.Employee.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return {"user": user, "role": "employee"}
    elif role == "hr":
        # For HR, we'll use a simple check (in production, you'd have a separate HR table)
        if user_id == 999:  # Special HR user ID
            return {"user": {"id": 999, "name": "HR Admin"}, "role": "hr"}
        else:
            raise HTTPException(status_code=404, detail="HR user not found")
    else:
        raise HTTPException(status_code=403, detail="Invalid role")

def require_employee(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "employee":
        raise HTTPException(status_code=403, detail="Employee access required")
    return current_user

def require_hr(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "hr":
        raise HTTPException(status_code=403, detail="HR access required")
    return current_user

def authenticate_employee(db: Session, email: str, employee_id: int):
    """Simple authentication for employees using email and ID"""
    employee = db.query(models.Employee).filter(
        models.Employee.email == email,
        models.Employee.id == employee_id
    ).first()
    return employee

def authenticate_hr(username: str, password: str):
    """Simple authentication for HR (hardcoded for MVP)"""
    # In production, this would check against a proper HR users table
    if username == "hr@company.com" and password == "hr123":
        return {"id": 999, "name": "HR Admin", "role": "hr"}
    return None

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
import uuid
from .config import settings

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password using bcrypt directly"""
    try:
        # Simple direct bcrypt check
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception as e:
        print(f"❌ Password verification error: {e}")
        return False

def get_password_hash(password: str) -> str:
    """Hash password using bcrypt directly"""
    try:
        # Clean password
        cleaned = password.strip()
        print(f"🔐 Hashing password of length: {len(cleaned)}")
        
        # Direct bcrypt hash
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(cleaned.encode('utf-8'), salt)
        
        # Return as string
        return hashed.decode('utf-8')
    except Exception as e:
        print(f"❌ Hashing error: {e}")
        # Ultimate fallback - truncate and try again
        truncated = password[:50].strip()
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(truncated.encode('utf-8'), salt).decode('utf-8')

def create_access_token(user_id: str) -> str:
    """Create a new access token"""
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "sub": str(user_id),
        "exp": expire,
        "type": "access",
        "jti": str(uuid.uuid4())
    }
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def create_refresh_token(user_id: str) -> str:
    """Create a new refresh token"""
    expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {
        "sub": str(user_id),
        "exp": expire,
        "type": "refresh",
        "jti": str(uuid.uuid4())
    }
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def decode_token(token: str, token_type: Optional[str] = None) -> dict:
    """Decode and validate a token"""
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        if token_type and payload.get("type") != token_type:
            raise ValueError(f"Invalid token type. Expected {token_type}")
        return payload
    except JWTError as e:
        raise ValueError(f"Invalid token: {str(e)}")

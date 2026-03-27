from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...core.security import verify_password, create_access_token, create_refresh_token, decode_token
from ...schemas.user import UserCreate, UserResponse, TokenResponse
from ...services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        print("=" * 50)
        print(f"📝 Registering user: {user_data.email}")
        print(f"🔑 Password length: {len(user_data.password)}")
        print(f"🔑 Password bytes: {len(user_data.password.encode('utf-8'))}")
        print(f"🔑 Full name: {user_data.full_name}")
        print("=" * 50)
        
        user = UserService.create_user(db, user_data)
        print(f"✅ User created successfully with ID: {user.id}")
        return user
    except ValueError as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login with email and password"""
    print("=" * 50)
    print(f"🔐 Login attempt: {form_data.username}")
    print("=" * 50)
    
    user = UserService.get_user_by_email(db, form_data.username)
    
    if not user:
        print(f"❌ User not found: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    print(f"✅ User found: {user.email}")
    print(f"🔑 Password verification...")
    
    if not verify_password(form_data.password, user.password_hash):
        print(f"❌ Password verification failed")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not user.is_active:
        print(f"❌ Account is inactive: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    print(f"✅ Password verified successfully")
    print(f"✅ Login successful for: {user.email}")
    
    return TokenResponse(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id)),
        token_type="bearer"
    )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    """Get new access token using refresh token"""
    print("=" * 50)
    print(f"🔄 Refresh token attempt")
    print("=" * 50)
    
    try:
        payload = decode_token(refresh_token, token_type="refresh")
        user_id = payload.get("sub")
        
        print(f"✅ Token decoded, user_id: {user_id}")
        
        user = UserService.get_user_by_id(db, user_id)
        if not user or not user.is_active:
            print(f"❌ User not found or inactive")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        print(f"✅ User found: {user.email}")
        print(f"✅ New tokens generated")
        
        return TokenResponse(
            access_token=create_access_token(str(user.id)),
            refresh_token=create_refresh_token(str(user.id)),
            token_type="bearer"
        )
    except ValueError as e:
        print(f"❌ Token validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

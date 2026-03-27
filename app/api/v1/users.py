from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ...schemas.user import UserResponse, UserUpdate
from ...api.deps import get_current_user
from ...models.user import User
from ...core.database import get_db
from ...services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: User = Depends(get_current_user)
):
    """
    👤 Get current logged in user info
    
    Returns:
    - User profile (email, name, plan, credits, etc.)
    
    🔐 Requires valid access token
    """
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_user_me(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ✏️ Update current user profile
    
    Fields that can be updated:
    - full_name
    - avatar_url
    
    🔐 Requires valid access token
    """
    updated_user = UserService.update_user(
        db, 
        str(current_user.id), 
        user_update.dict(exclude_unset=True)
    )
    return updated_user

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    🗑️ Delete current user account
    - Soft delete (deactivate account)
    - All user data will be anonymized
    
    🔐 Requires valid access token
    """
    # Soft delete - deactivate account
    current_user.is_active = False
    current_user.email = f"deleted_{current_user.id}@deleted.user"
    current_user.full_name = "Deleted User"
    db.commit()
    
    return None

@router.get("/", response_model=List[UserResponse])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    📋 Get all users (Admin only)
    - Pagination supported
    - Only accessible by admin users
    
    🔐 Requires valid access token + admin privileges
    """
    # TODO: Add admin check
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    🔍 Get user by ID (Admin only)
    
    🔐 Requires valid access token + admin privileges
    """
    # TODO: Add admin check
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

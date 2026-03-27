from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.video import (
    VideoResponse, 
    VideoUploadResponse,
    VideoUpdate,
    VideoStatus
)
from app.services.video_service import VideoService

router = APIRouter(prefix="/videos", tags=["Videos"])

@router.post("/upload", response_model=VideoUploadResponse)
async def upload_video(
    file: UploadFile = File(...),
    title: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    🎬 Upload a video for processing
    
    - Validates file type and size
    - Checks user credits
    - Saves file and creates project
    - Queues for AI processing
    
    Returns:
    - project_id: UUID of created project
    - message: Status message
    - status: Current status (pending)
    """
    try:
        project = await VideoService.create_project(
            db=db,
            user_id=str(current_user.id),
            file=file,
            title=title
        )
        
        return VideoUploadResponse(
            project_id=project.id,
            message="Video uploaded successfully and queued for processing",
            status=project.status.value
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/projects", response_model=List[VideoResponse])
async def get_user_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    📋 Get all video projects for current user
    
    - Pagination supported (skip, limit)
    - Returns list of projects with details
    - Sorted by creation date (newest first)
    """
    projects = VideoService.get_user_projects(
        db=db,
        user_id=str(current_user.id),
        skip=skip,
        limit=limit
    )
    return projects

@router.get("/projects/{project_id}", response_model=VideoResponse)
async def get_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    🔍 Get a specific video project by ID
    
    Returns:
    - Full project details including status
    - Source and processed file URLs
    """
    project = VideoService.get_project(
        db=db,
        project_id=str(project_id),
        user_id=str(current_user.id)
    )
    return project

@router.put("/projects/{project_id}", response_model=VideoResponse)
async def update_project(
    project_id: UUID,
    project_update: VideoUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ✏️ Update video project metadata
    
    Fields that can be updated:
    - title
    - description
    - settings
    """
    project = VideoService.get_project(
        db=db,
        project_id=str(project_id),
        user_id=str(current_user.id)
    )
    
    # Update fields
    if project_update.title is not None:
        project.title = project_update.title
    if project_update.description is not None:
        project.description = project_update.description
    if project_update.settings is not None:
        project.settings = project_update.settings
    
    db.commit()
    db.refresh(project)
    
    return project

@router.delete("/projects/{project_id}")
async def delete_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    🗑️ Delete a video project
    
    - Deletes database record
    - Removes associated files from disk
    """
    result = VideoService.delete_project(
        db=db,
        project_id=str(project_id),
        user_id=str(current_user.id)
    )
    return result

@router.get("/projects/{project_id}/status")
async def get_project_status(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ⏳ Get current processing status of a video
    
    Returns:
    - status: pending/processing/completed/failed
    - created_at: When project was created
    - updated_at: Last status update
    """
    project = VideoService.get_project(
        db=db,
        project_id=str(project_id),
        user_id=str(current_user.id)
    )
    
    return {
        "project_id": project.id,
        "status": project.status.value,
        "created_at": project.created_at,
        "updated_at": project.updated_at
    }

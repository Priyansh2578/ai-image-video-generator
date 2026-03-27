from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.image import (
    ImageResponse,
    ImageUploadResponse,
    ImageUpdate,
    FilterApplyRequest,
    ImageResizeRequest,
    ImageCropRequest
)
from app.services.image_service import ImageService

router = APIRouter(prefix="/images", tags=["Images"])

@router.post("/upload", response_model=ImageUploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    title: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    🖼️ Upload an image for editing
    
    - Validates file type and size
    - Saves file and creates project
    - Returns project ID
    
    Supported formats: jpg, jpeg, png, gif, webp, bmp, tiff
    """
    try:
        project = await ImageService.create_project(
            db=db,
            user_id=str(current_user.id),
            file=file,
            title=title
        )
        
        return ImageUploadResponse(
            project_id=project.id,
            message="Image uploaded successfully",
            status=project.status.value
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/projects", response_model=List[ImageResponse])
async def get_user_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """📋 Get all image projects for current user"""
    projects = ImageService.get_user_projects(
        db=db,
        user_id=str(current_user.id),
        skip=skip,
        limit=limit
    )
    return projects

@router.get("/projects/{project_id}", response_model=ImageResponse)
async def get_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """🔍 Get a specific image project by ID"""
    project = ImageService.get_project(
        db=db,
        project_id=str(project_id),
        user_id=str(current_user.id)
    )
    return project

@router.put("/projects/{project_id}", response_model=ImageResponse)
async def update_project(
    project_id: UUID,
    project_update: ImageUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """✏️ Update image project metadata"""
    project = ImageService.get_project(db, str(project_id), str(current_user.id))
    
    if project_update.title is not None:
        project.title = project_update.title
    if project_update.description is not None:
        project.description = project_update.description
    
    db.commit()
    db.refresh(project)
    return project

@router.delete("/projects/{project_id}")
async def delete_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """🗑️ Delete an image project"""
    result = ImageService.delete_project(
        db=db,
        project_id=str(project_id),
        user_id=str(current_user.id)
    )
    return result

@router.post("/projects/{project_id}/filter", response_model=ImageResponse)
async def apply_filter(
    project_id: UUID,
    filter_request: FilterApplyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """🎨 Apply a filter to an image
    
    Available filters:
    - grayscale/bw: Black and white
    - sepia: Sepia tone
    - blur: Gaussian blur
    - contour: Contour effect
    - emboss: Emboss effect
    - edge_enhance: Edge enhancement
    - sharpen: Sharpen image
    - smooth: Smooth image
    - invert: Invert colors
    """
    project = ImageService.apply_filter(
        db=db,
        project_id=str(project_id),
        user_id=str(current_user.id),
        filter_name=filter_request.filter_name,
        parameters=filter_request.parameters
    )
    return project

@router.post("/projects/{project_id}/resize", response_model=ImageResponse)
async def resize_image(
    project_id: UUID,
    resize_request: ImageResizeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """📏 Resize an image"""
    project = ImageService.resize_image(
        db=db,
        project_id=str(project_id),
        user_id=str(current_user.id),
        width=resize_request.width,
        height=resize_request.height,
        maintain_aspect=resize_request.maintain_aspect
    )
    return project

@router.post("/projects/{project_id}/crop", response_model=ImageResponse)
async def crop_image(
    project_id: UUID,
    crop_request: ImageCropRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """✂️ Crop an image"""
    project = ImageService.crop_image(
        db=db,
        project_id=str(project_id),
        user_id=str(current_user.id),
        x=crop_request.x,
        y=crop_request.y,
        width=crop_request.width,
        height=crop_request.height
    )
    return project

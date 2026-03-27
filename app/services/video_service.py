import os
import uuid
from pathlib import Path
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException
from datetime import datetime
from ..models.video import VideoProject
from ..models.user import User
from ..schemas.video import VideoCreate, VideoStatus
from ..core.config import settings
import logging

logger = logging.getLogger(__name__)

class VideoService:
    
    @staticmethod
    async def create_project(
        db: Session,
        user_id: str,
        file: UploadFile,
        title: str = None
    ) -> VideoProject:
        """
        🎬 Create a new video project
        
        Steps:
        1. Validate file type and size
        2. Check user credits
        3. Save file to disk
        4. Create database record
        5. Queue for processing
        """
        
        # 1. Validate file type
        allowed_types = settings.ALLOWED_VIDEO_TYPES
        file_ext = file.filename.split('.')[-1].lower()
        
        if file_ext not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed. Allowed types: {allowed_types}"
            )
        
        # 2. Check file size
        file_size = 0
        content = await file.read()
        file_size = len(content)
        await file.seek(0)  # Reset file pointer
        
        if file_size > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Max size: {settings.MAX_UPLOAD_SIZE / (1024*1024)}MB"
            )
        
        # 3. Check user credits
        user = db.query(User).filter(User.id == user_id).first()
        if user.credits_remaining <= 0:
            raise HTTPException(
                status_code=402,
                detail="No credits remaining. Please upgrade your plan."
            )
        
        # 4. Save file to disk
        upload_dir = Path("static/uploads/videos")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_name = f"{uuid.uuid4()}.{file_ext}"
        file_path = upload_dir / file_name
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        # 5. Create database record
        project = VideoProject(
            id=uuid.uuid4(),
            user_id=user_id,
            title=title or file.filename,
            source_file=str(file_path),
            file_size=file_size,
            status=VideoStatus.PENDING
        )
        
        db.add(project)
        db.commit()
        db.refresh(project)
        
        # 6. Deduct credit
        user.credits_remaining -= 1
        db.commit()
        
        logger.info(f"✅ Video project created: {project.id} for user {user_id}")
        
        # 7. Queue for processing (TODO: Add Celery task)
        # process_video_task.delay(str(project.id), str(file_path))
        
        return project
    
    @staticmethod
    def get_project(db: Session, project_id: str, user_id: str) -> VideoProject:
        """Get a specific video project"""
        project = db.query(VideoProject).filter(
            VideoProject.id == project_id,
            VideoProject.user_id == user_id
        ).first()
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return project
    
    @staticmethod
    def get_user_projects(
        db: Session,
        user_id: str,
        skip: int = 0,
        limit: int = 20
    ) -> list[VideoProject]:
        """Get all projects for a user"""
        return db.query(VideoProject).filter(
            VideoProject.user_id == user_id
        ).order_by(
            VideoProject.created_at.desc()
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def delete_project(db: Session, project_id: str, user_id: str):
        """Delete a video project"""
        project = VideoService.get_project(db, project_id, user_id)
        
        # Delete file from disk
        if project.source_file and os.path.exists(project.source_file):
            os.remove(project.source_file)
        
        if project.processed_file and os.path.exists(project.processed_file):
            os.remove(project.processed_file)
        
        db.delete(project)
        db.commit()
        
        logger.info(f"🗑️ Project deleted: {project_id}")
        return {"message": "Project deleted successfully"}
    
    @staticmethod
    def update_project_status(
        db: Session,
        project_id: str,
        status: VideoStatus,
        processed_file: str = None
    ):
        """Update project status (used by background tasks)"""
        project = db.query(VideoProject).filter(
            VideoProject.id == project_id
        ).first()
        
        if project:
            project.status = status
            if processed_file:
                project.processed_file = processed_file
            project.updated_at = datetime.utcnow()
            db.commit()
            
        return project

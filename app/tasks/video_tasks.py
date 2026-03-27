from celery import shared_task
from app.core.database import SessionLocal
from app.models.video import VideoProject, VideoStatus
from app.services.storage_service import storage
import logging
import time
import os
import shutil

logger = logging.getLogger(__name__)

@shared_task(bind=True, name="process_video")
def process_video_task(self, project_id: str, user_id: str):
    """
    🎬 Background task for video processing
    
    States:
    - PENDING → PROCESSING → COMPLETED/FAILED
    """
    db = SessionLocal()
    try:
        # Get project
        project = db.query(VideoProject).filter(VideoProject.id == project_id).first()
        if not project:
            logger.error(f"❌ Project {project_id} not found")
            return
        
        # Update status to PROCESSING
        project.status = VideoStatus.PROCESSING
        db.commit()
        logger.info(f"🎬 Processing video: {project_id} for user {user_id}")
        
        # Simulate processing time (replace with actual video processing)
        time.sleep(5)
        
        # Generate output file path
        output_filename = f"processed/video_{project_id}.mp4"
        output_path = storage.base_path / output_filename
        
        # Ensure directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # For now, just copy the source file (replace with actual processing)
        if os.path.exists(project.source_file):
            shutil.copy2(project.source_file, output_path)
        
        # Update project with processed file
        project.processed_file = str(output_path)
        project.status = VideoStatus.COMPLETED
        db.commit()
        
        logger.info(f"✅ Video processed successfully: {project_id}")
        
        return {
            "project_id": project_id,
            "status": "completed",
            "processed_file": str(output_path)
        }
        
    except Exception as e:
        logger.error(f"❌ Video processing failed for {project_id}: {str(e)}")
        
        # Update status to FAILED
        if project:
            project.status = VideoStatus.FAILED
            db.commit()
        
        # Retry logic
        self.retry(exc=e, countdown=60, max_retries=3)
        
    finally:
        db.close()

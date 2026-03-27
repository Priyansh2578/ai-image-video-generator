from celery import shared_task
from app.core.database import SessionLocal
from app.models.image import ImageProject, ImageStatus
from PIL import Image
import logging
import os

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def process_image_task(self, project_id: str, user_id: str, filter_name: str = None):
    db = SessionLocal()
    try:
        project = db.query(ImageProject).filter(ImageProject.id == project_id).first()
        if not project:
            return
        project.status = ImageStatus.PROCESSING
        db.commit()

        img = Image.open(project.source_file)
        if filter_name == "grayscale":
            img = img.convert('L').convert('RGB')
        elif filter_name == "blur":
            from PIL import ImageFilter
            img = img.filter(ImageFilter.BLUR)

        out_path = f"processed/image_{project_id}.jpg"
        img.save(out_path)
        project.processed_file = out_path
        project.status = ImageStatus.COMPLETED
        db.commit()
    except Exception as e:
        project.status = ImageStatus.FAILED
        db.commit()
        raise
    finally:
        db.close()

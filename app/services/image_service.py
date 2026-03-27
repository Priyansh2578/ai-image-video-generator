import os
import uuid
from pathlib import Path
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException
from datetime import datetime
from PIL import Image
import io
from ..models.image import ImageProject, ImageStatus
from ..models.user import User
from ..schemas.image import ImageCreate, ImageFilter, ImageResizeRequest, ImageCropRequest
from ..core.config import settings
import logging

logger = logging.getLogger(__name__)

class ImageService:
    
    ALLOWED_IMAGE_TYPES = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'tiff']
    
    @staticmethod
    async def create_project(
        db: Session,
        user_id: str,
        file: UploadFile,
        title: str = None
    ) -> ImageProject:
        """
        🖼️ Create a new image project
        
        Steps:
        1. Validate file type and size
        2. Check user credits
        3. Save file to disk
        4. Get image metadata
        5. Create database record
        """
        
        # 1. Validate file type
        file_ext = file.filename.split('.')[-1].lower()
        
        if file_ext not in ImageService.ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed. Allowed types: {ImageService.ALLOWED_IMAGE_TYPES}"
            )
        
        # 2. Check file size
        content = await file.read()
        file_size = len(content)
        await file.seek(0)
        
        max_size = 50 * 1024 * 1024  # 50MB max for images
        if file_size > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Max size: 50MB"
            )
        
        # 3. Check user credits (optional - decide if images also use credits)
        user = db.query(User).filter(User.id == user_id).first()
        # Uncomment if you want to use credits for images too
        # if user.credits_remaining <= 0:
        #     raise HTTPException(
        #         status_code=402,
        #         detail="No credits remaining. Please upgrade your plan."
        #     )
        
        # 4. Get image metadata
        try:
            img = Image.open(io.BytesIO(content))
            width, height = img.size
            img_format = img.format.lower() if img.format else file_ext
        except Exception as e:
            logger.error(f"Failed to read image metadata: {e}")
            width, height = 0, 0
            img_format = file_ext
        
        # 5. Save file to disk
        upload_dir = Path("static/uploads/images")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_name = f"{uuid.uuid4()}.{file_ext}"
        file_path = upload_dir / file_name
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        # 6. Create database record
        project = ImageProject(
            id=uuid.uuid4(),
            user_id=user_id,
            title=title or file.filename,
            source_file=str(file_path),
            file_size=file_size,
            width=width,
            height=height,
            format=img_format,
            status=ImageStatus.COMPLETED  # Images are ready immediately
        )
        
        db.add(project)
        db.commit()
        db.refresh(project)
        
        # 7. Deduct credit if needed (uncomment if using credits)
        # user.credits_remaining -= 1
        # db.commit()
        
        logger.info(f"✅ Image project created: {project.id} for user {user_id}")
        
        return project
    
    @staticmethod
    def get_project(db: Session, project_id: str, user_id: str) -> ImageProject:
        """Get a specific image project"""
        project = db.query(ImageProject).filter(
            ImageProject.id == project_id,
            ImageProject.user_id == user_id
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
    ) -> list[ImageProject]:
        """Get all image projects for a user"""
        return db.query(ImageProject).filter(
            ImageProject.user_id == user_id
        ).order_by(
            ImageProject.created_at.desc()
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def delete_project(db: Session, project_id: str, user_id: str):
        """Delete an image project"""
        project = ImageService.get_project(db, project_id, user_id)
        
        # Delete file from disk
        if project.source_file and os.path.exists(project.source_file):
            os.remove(project.source_file)
        
        if project.processed_file and os.path.exists(project.processed_file):
            os.remove(project.processed_file)
        
        db.delete(project)
        db.commit()
        
        logger.info(f"🗑️ Image project deleted: {project_id}")
        return {"message": "Project deleted successfully"}
    
    @staticmethod
    def apply_filter(
        db: Session,
        project_id: str,
        user_id: str,
        filter_name: str,
        parameters: dict = None
    ) -> ImageProject:
        """Apply a filter to an image"""
        project = ImageService.get_project(db, project_id, user_id)
        
        # Open the image
        try:
            img = Image.open(project.source_file)
            
            # Apply filter based on name
            if filter_name == "grayscale" or filter_name == "bw":
                img = img.convert('L').convert('RGB')
            elif filter_name == "sepia":
                # Sepia filter implementation
                sepia = Image.new('RGB', img.size)
                # Simple sepia effect
                pixels = img.load()
                sepia_pixels = sepia.load()
                for i in range(img.width):
                    for j in range(img.height):
                        r, g, b = pixels[i, j][:3]
                        tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                        tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                        tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                        sepia_pixels[i, j] = (min(tr, 255), min(tg, 255), min(tb, 255))
                img = sepia
            elif filter_name == "blur":
                from PIL import ImageFilter
                img = img.filter(ImageFilter.BLUR)
            elif filter_name == "contour":
                from PIL import ImageFilter
                img = img.filter(ImageFilter.CONTOUR)
            elif filter_name == "emboss":
                from PIL import ImageFilter
                img = img.filter(ImageFilter.EMBOSS)
            elif filter_name == "edge_enhance":
                from PIL import ImageFilter
                img = img.filter(ImageFilter.EDGE_ENHANCE)
            elif filter_name == "sharpen":
                from PIL import ImageFilter
                img = img.filter(ImageFilter.SHARPEN)
            elif filter_name == "smooth":
                from PIL import ImageFilter
                img = img.filter(ImageFilter.SMOOTH)
            elif filter_name == "invert":
                from PIL import ImageOps
                img = ImageOps.invert(img.convert('RGB'))
            
            # Save processed image
            output_dir = Path("static/processed/images")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            output_file = output_dir / f"filtered_{project_id}_{filter_name}.jpg"
            img.save(output_file, format='JPEG', quality=95)
            
            # Update project
            project.processed_file = str(output_file)
            project.filters_applied = project.filters_applied + [filter_name]
            project.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(project)
            
            logger.info(f"✅ Filter '{filter_name}' applied to project {project_id}")
            
        except Exception as e:
            logger.error(f"❌ Error applying filter: {e}")
            raise HTTPException(status_code=500, detail=f"Error applying filter: {str(e)}")
        
        return project
    
    @staticmethod
    def resize_image(
        db: Session,
        project_id: str,
        user_id: str,
        width: int,
        height: int,
        maintain_aspect: bool = True
    ) -> ImageProject:
        """Resize an image"""
        project = ImageService.get_project(db, project_id, user_id)
        
        try:
            img = Image.open(project.source_file)
            
            if maintain_aspect:
                img.thumbnail((width, height), Image.Resampling.LANCZOS)
            else:
                img = img.resize((width, height), Image.Resampling.LANCZOS)
            
            # Save resized image
            output_dir = Path("static/processed/images")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            output_file = output_dir / f"resized_{project_id}.jpg"
            img.save(output_file, format='JPEG', quality=95)
            
            # Update project
            project.processed_file = str(output_file)
            project.width = img.width
            project.height = img.height
            project.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(project)
            
            logger.info(f"✅ Image resized for project {project_id}")
            
        except Exception as e:
            logger.error(f"❌ Error resizing image: {e}")
            raise HTTPException(status_code=500, detail=f"Error resizing image: {str(e)}")
        
        return project
    
    @staticmethod
    def crop_image(
        db: Session,
        project_id: str,
        user_id: str,
        x: int,
        y: int,
        width: int,
        height: int
    ) -> ImageProject:
        """Crop an image"""
        project = ImageService.get_project(db, project_id, user_id)
        
        try:
            img = Image.open(project.source_file)
            cropped = img.crop((x, y, x + width, y + height))
            
            # Save cropped image
            output_dir = Path("static/processed/images")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            output_file = output_dir / f"cropped_{project_id}.jpg"
            cropped.save(output_file, format='JPEG', quality=95)
            
            # Update project
            project.processed_file = str(output_file)
            project.width = cropped.width
            project.height = cropped.height
            project.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(project)
            
            logger.info(f"✅ Image cropped for project {project_id}")
            
        except Exception as e:
            logger.error(f"❌ Error cropping image: {e}")
            raise HTTPException(status_code=500, detail=f"Error cropping image: {str(e)}")
        
        return project

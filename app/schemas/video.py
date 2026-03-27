from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

class VideoStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class VideoBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class VideoCreate(VideoBase):
    pass

class VideoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None

class VideoResponse(VideoBase):
    id: UUID
    user_id: UUID
    status: VideoStatus
    source_file: Optional[str]
    processed_file: Optional[str]
    thumbnail_url: Optional[str]
    duration: Optional[int]
    resolution: Optional[str]
    file_size: Optional[int]
    settings: Dict[str, Any] = {}
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class VideoUploadResponse(BaseModel):
    project_id: UUID
    message: str
    status: str

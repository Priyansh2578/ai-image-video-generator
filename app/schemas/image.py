from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

class ImageStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class ImageBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class ImageCreate(ImageBase):
    pass

class ImageUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    filters_applied: Optional[List[str]] = None
    settings: Optional[Dict[str, Any]] = None

class ImageResponse(ImageBase):
    id: UUID
    user_id: UUID
    status: ImageStatus
    source_file: Optional[str]
    processed_file: Optional[str]
    thumbnail_url: Optional[str]
    file_size: Optional[int]
    width: Optional[int]
    height: Optional[int]
    format: Optional[str]
    filters_applied: List[str] = []
    settings: Dict[str, Any] = {}
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class ImageUploadResponse(BaseModel):
    project_id: UUID
    message: str
    status: str

# ✅ ये class add kiya
class FilterApplyRequest(BaseModel):
    filter_name: str
    parameters: Optional[Dict[str, Any]] = None

# ✅ ये class add kiya
class ImageResizeRequest(BaseModel):
    width: int
    height: int
    maintain_aspect: bool = True

# ✅ ये class add kiya
class ImageCropRequest(BaseModel):
    x: int
    y: int
    width: int
    height: int

class ImageFilter(BaseModel):
    name: str
    parameters: Dict[str, Any] = {}

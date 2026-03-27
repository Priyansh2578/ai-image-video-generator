from sqlalchemy import Column, String, Integer, DateTime, JSON, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum
from ..core.database import Base

class ImageStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class ImageProject(Base):
    __tablename__ = "image_projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255))
    description = Column(String)
    status = Column(Enum(ImageStatus), default=ImageStatus.PENDING, nullable=False)
    source_file = Column(String(512))
    processed_file = Column(String(512))
    thumbnail_url = Column(String(512))
    file_size = Column(Integer)
    width = Column(Integer)
    height = Column(Integer)
    format = Column(String(20))
    filters_applied = Column(JSON, default=[])
    settings = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<ImageProject {self.id} - {self.title}>"

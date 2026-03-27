import os
import uuid
from pathlib import Path
from fastapi import UploadFile

class LocalStorageService:
    def __init__(self, base_path: str = "static"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def save(self, file: UploadFile, folder: str) -> str:
        folder_path = self.base_path / folder
        folder_path.mkdir(parents=True, exist_ok=True)
        ext = file.filename.split('.')[-1]
        filename = f"{uuid.uuid4()}.{ext}"
        file_path = folder_path / filename
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        return str(file_path)

    def get_url(self, path: str) -> str:
        return f"/static/{path}"

    def delete(self, path: str):
        if os.path.exists(path):
            os.remove(path)

storage = LocalStorageService()

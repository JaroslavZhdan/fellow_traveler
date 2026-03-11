import os
from core.config import settings
from fastapi import UploadFile
from uuid import uuid4
import aiofiles

async def save_car_image(car_id: int, upload: UploadFile) -> str:
    ext = os.path.splitext(upload.filename)[1]
    filename = f"{uuid4().hex}{ext}"
    dirpath = os.path.join(settings.UPLOAD_DIR, "cars", str(car_id))
    os.makedirs(dirpath, exist_ok=True)
    path = os.path.join(dirpath, filename)
    async with aiofiles.open(path, "wb") as f:
        content = await upload.read()
        await f.write(content)
    return f"/uploads/cars/{car_id}/{filename}"

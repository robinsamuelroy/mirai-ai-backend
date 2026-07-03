import os
import uuid
import aiofiles
from fastapi import UploadFile, HTTPException, status
from app.core.config import settings

ALLOWED_MIME_TYPES = {"application/pdf"}
ALLOWED_EXTENSIONS = {".pdf"}

def validate_file(file: UploadFile) -> None:
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Only PDF files are accepted."
        )
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File extension not allowed. Only .pdf files are accepted."
        )
    
def generate_stored_filename(original_filename: str) -> str:
    ext = os.path.splitext(original_filename)[1].lower()
    unique_id = str(uuid.uuid4())[:8]
    clean_name = original_filename.replace(" ", "_").lower()
    return f"{unique_id}_{clean_name}"

def get_user_upload_dir(user_id: int) -> str:
    user_dir = os.path.join(settings.UPLOAD_DIR, f"user_{user_id}")
    os.makedirs(user_dir, exist_ok=True)
    return user_dir

async def save_file_to_disk(file: UploadFile, user_id: int) -> dict:
    content = await file.read()
    file_size = len(content)
    if file_size > settings.MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size is {settings.MAX_FILE_SIZE_MB}MB."
        )

    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty."
        )
    # generate unique filename and build full path
    stored_filename = generate_stored_filename(file.filename)
    user_dir = get_user_upload_dir(user_id)
    file_path = os.path.join(user_dir, stored_filename)

    # write file to disk asynchronously
    # aiofiles → non-blocking file I/O, doesn't block other requests
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    return {
        "original_filename": file.filename,
        "stored_filename": stored_filename,
        "file_path": file_path,
        "file_size": file_size,
        "mime_type": file.content_type,
    }
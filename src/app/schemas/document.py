from pydantic import BaseModel
from datetime import datetime

class DocumentResponse(BaseModel):
    id: int
    user_id: int
    original_filename: str
    stored_filename: str
    file_size: int
    mime_type: str
    is_processed: str
    created_at: datetime

    class Config:
        from_attributes = True
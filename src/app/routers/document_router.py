from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.document import DocumentResponse
from app.services.document_service import document_service
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


@router.post("/upload", response_model=DocumentResponse, status_code=201)
async def upload_document( file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await document_service.upload_document(db, file, current_user)

@router.post("/{document_id}/process", response_model=DocumentResponse)
async def process_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Triggers the full processing pipeline:
    Extract → Chunk → Embed → Store in ChromaDB
    After this, the document is searchable.
    """
    return await document_service.process_document(db, document_id, current_user)


@router.get("/", response_model=list[DocumentResponse])
def get_my_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return document_service.get_user_documents(db, current_user)


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return document_service.get_document(db, document_id, current_user)


@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return document_service.delete_document(db, document_id, current_user)
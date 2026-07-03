from sqlalchemy.orm import Session
from app.models.document import Document

class DocumentRepository:
    def create(self, db: Session, user_id: int, file_meta: dict) -> Document:
        document = Document(
            user_id=user_id,
            original_filename=file_meta["original_filename"],
            stored_filename=file_meta["stored_filename"],
            file_path=file_meta["file_path"],
            file_size=file_meta["file_size"],
            mime_type=file_meta["mime_type"],
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        return document
    
    def get_by_id(self, db: Session, document_id: int) -> Document | None:
        return db.query(Document).filter(Document.id == document_id).first()
    
    def get_user_documents(self, db: Session, user_id: int) -> list[Document]:
        return (
            db.query(Document)
            .filter(Document.user_id == user_id)
            .order_by(Document.created_at.desc())
            .all()
        )
    
    def delete(self, db: Session, document: Document) -> None:
        db.delete(document)
        db.commit()

    def update_status(self, db: Session, document_id: int, status: str) -> Document:
        document = self.get_by_id(db, document_id)
        document.is_processed = status
        db.commit()
        db.refresh(document)
        return document

document_repository = DocumentRepository()




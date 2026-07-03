import os
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from app.repositories.document_repository import document_repository
from app.utils.file_handler import validate_file, save_file_to_disk
from app.utils.pdf_extractor import extract_text_from_pdf
from app.utils.chunker import chunk_text
from app.utils.embeddings import generate_embeddings_batch
from app.core.chromadb_client import get_user_collection
from app.models.user import User
from app.models.document import Document


class DocumentService:

    async def upload_document(self, db: Session, file: UploadFile, current_user: User) -> Document:
        validate_file(file)
        file_meta = await save_file_to_disk(file, current_user.id)
        document = document_repository.create(db, current_user.id, file_meta)
        return document
    
    async def process_document(self, db: Session, document_id: int, current_user: User) -> Document:
        """
        Full pipeline:
        1. Extract text from PDF
        2. Chunk the text
        3. Generate embeddings for each chunk
        4. Store in ChromaDB
        5. Update document status in PostgreSQL
        """
        # fetch and verify ownership
        document = self.get_document(db, document_id, current_user)

        if document.is_processed == "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document already processed"
            )

        try:
            # mark as processing
            document_repository.update_status(db, document_id, "processing")

            # step 1 — extract text
            raw_text = extract_text_from_pdf(document.file_path)

            # step 2 — chunk text
            chunks = chunk_text(raw_text)

            if not chunks:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No content could be extracted from document"
                )

            # step 3 — generate embeddings in batch (fast)
            chunk_texts = [c["content"] for c in chunks]
            embeddings = generate_embeddings_batch(chunk_texts)

            # step 4 — store in ChromaDB
            collection = get_user_collection(current_user.id)

            collection.add(
                ids=[
                    f"doc_{document_id}_chunk_{c['chunk_index']}"
                    for c in chunks
                ],
                embeddings=embeddings,
                documents=chunk_texts,
                # original text — ChromaDB stores this alongside the vector

                metadatas=[
                    {
                        "document_id": document_id,
                        "chunk_index": c["chunk_index"],
                        "original_filename": document.original_filename,
                        "char_start": c["char_start"],
                        "char_end": c["char_end"],
                    }
                    for c in chunks
                ]
                # metadata — lets us filter searches later
                # e.g. "only search chunks from document_id=5"
            )

            # step 5 — mark as completed
            document = document_repository.update_status(db, document_id, "completed")
            return document

        except HTTPException:
            document_repository.update_status(db, document_id, "failed")
            raise

        except Exception as e:
            document_repository.update_status(db, document_id, "failed")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Processing failed: {str(e)}"
            )

    def get_user_documents(self, db: Session, current_user: User) -> list[Document]:
        return document_repository.get_user_documents(db, current_user.id)

    def get_document(self, db: Session, document_id: int, current_user: User) -> Document:
        document = document_repository.get_by_id(db, document_id)

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        # ownership check
        if document.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this document")
        return document

    def delete_document(self, db: Session, document_id: int, current_user: User) -> dict:
        document = self.get_document(db, document_id, current_user)
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
        # then delete record from database
        document_repository.delete(db, document)
        return {"message": "Document deleted successfully"}

document_service = DocumentService()



# the document returning will be,

# collection.add(

# ids=[

# "doc_15_chunk_0",

# "doc_15_chunk_1"

# ],

# documents=[

# "Python is a programming language.",

# "Variables store values."

# ],

# embeddings=[

# [0.12,0.55,...],

# [0.93,0.14,...]

# ],

# metadatas=[

# {

# "document_id":15,

# "chunk_index":0,

# ...

# },

# {

# "document_id":15,

# "chunk_index":1,

# ...

# }

# ]

# )
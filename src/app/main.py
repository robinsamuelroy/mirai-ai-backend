# src/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import Base, engine
from app.models import User, Chat, Message, Document
from app.routers import user_router, chat_router, document_router, search_router,rag_router

def create_application() -> FastAPI:
    Base.metadata.create_all(bind=engine)

    application = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # register routers
    application.include_router(user_router, prefix=settings.API_V1_STR)
    application.include_router(chat_router, prefix=settings.API_V1_STR)
    application.include_router(document_router, prefix=settings.API_V1_STR)
    application.include_router(search_router, prefix=settings.API_V1_STR)
    application.include_router(rag_router, prefix=settings.API_V1_STR)

    return application


app = create_application()


@app.get("/")
def health_check():
    return {
        "status": "running",
        "project": settings.PROJECT_NAME,
    }
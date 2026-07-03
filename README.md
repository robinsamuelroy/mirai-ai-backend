# AI Knowledge Assistant

A production-ready RAG (Retrieval Augmented Generation) backend built with FastAPI.
Upload PDFs, ask questions, get AI-powered answers grounded in your documents.

## Tech Stack

- **FastAPI** — async Python web framework
- **PostgreSQL** — relational database
- **ChromaDB** — vector store for semantic search
- **Sentence Transformers** — local embedding generation
- **Google Gemini** — LLM for answer generation
- **Docker** — containerized deployment

## Features

- JWT Authentication (register, login, protected routes)
- PDF upload and text extraction
- Automatic text chunking and embedding
- Semantic similarity search
- RAG pipeline with conversation memory
- Multi-user support with data isolation
- Chat history persistence

## Architecture
- Request → Router → Service → Repository → PostgreSQL
- → ChromaDB (vector search)
- → Gemini (answer generation)
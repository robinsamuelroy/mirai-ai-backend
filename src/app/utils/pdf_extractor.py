# src/app/utils/pdf_extractor.py

import re
from PyPDF2 import PdfReader
from fastapi import HTTPException, status


def extract_text_from_pdf(file_path: str) -> str:
    """
    Reads a PDF from disk and extracts all text from every page.
    Returns a single cleaned string.
    """
    try:
        reader = PdfReader(file_path)

        if len(reader.pages) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="PDF has no pages"
            )

        all_text = []

        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()

            if text:
                # tag each page so we know where text came from later
                # useful for citations in RAG responses
                all_text.append(f"[Page {page_num + 1}]\n{text}")

        if not all_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No text could be extracted. PDF may be scanned or image-based."
            )

        raw_text = "\n\n".join(all_text)
        return clean_text(raw_text)

    except HTTPException:
        raise  # re-raise our own exceptions as-is

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read PDF: {str(e)}"
        )


def clean_text(text: str) -> str:
    # replace multiple newlines with double newline (paragraph break)
    text = re.sub(r'\n{3,}', '\n\n', text)
    # replace multiple spaces with single space
    text = re.sub(r' {2,}', ' ', text)
    # remove non-printable characters except newlines and tabs
    text = re.sub(r'[^\x20-\x7E\n\t]', '', text)
    # strip leading/trailing whitespace from each line
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)

    return text.strip()


def get_page_count(file_path: str) -> int:
    """Returns the number of pages in a PDF"""
    try:
        reader = PdfReader(file_path)
        return len(reader.pages)
    except Exception:
        return 0
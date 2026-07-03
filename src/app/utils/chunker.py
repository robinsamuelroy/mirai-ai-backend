from langchain_text_splitters import RecursiveCharacterTextSplitter

def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> list[dict]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = splitter.split_text(text)
    result = []
    char_position = 0

    for index, chunk_content in enumerate(chunks):
        char_start = text.find(chunk_content, char_position)
        char_end = char_start + len(chunk_content)

        result.append({
            "chunk_index": index,
            "content": chunk_content,
            "char_start": char_start,
            "char_end": char_end,
        })

        char_position = char_start + 1

    return result
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List
from langchain_core.documents import Document

def load_and_split_pdf(file_path: str) -> List[Document]:
    """
    Loads a PDF file and splits its content into overlapping text chunks.
    This ensures better context retention during retrieval and generation.
    
    Args:
        file_path (str): The local path to the PDF file.

    Returns:
        List[Document]: A list of text chunks as LangChain Document objects.
    """
    # Step 1: Load the PDF using PyPDFLoader
    loader = PyPDFLoader(file_path)
    documents = loader.load()

    print(f"📄 Loaded {len(documents)} pages from PDF.")

    # Step 2: Split documents into chunks with overlap to retain context
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,      # large enough to capture full paragraphs or bullet points
        chunk_overlap=200,    # retain overlap so no context is cut mid-way
        separators=["\n\n", "\n", ".", " "]  # prioritize semantic breaks
    )
    chunks = text_splitter.split_documents(documents)

    print(f"✂️ Split into {len(chunks)} chunks.")
    
    # Optional: debug print a few chunks
    for i, chunk in enumerate(chunks[:3]):
        print(f"🔹 Chunk {i} preview:\n{chunk.page_content[:300]}...\n")

    return chunks
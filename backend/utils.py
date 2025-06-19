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
    try:
        # ✅ Step 1: Load the PDF using LangChain's PyPDFLoader
        loader = PyPDFLoader(file_path)
        documents = loader.load()

        print(f"📄 Loaded {len(documents)} pages from PDF.")

        # ✅ Step 2: Split documents into context-preserving chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,       # Each chunk ~1000 characters
            chunk_overlap=200,     # 200-character overlap to avoid context break
            separators=["\n\n", "\n", ".", " "]  # Semantic breaks prioritized
        )

        chunks = text_splitter.split_documents(documents)
        print(f"✂️ Split into {len(chunks)} chunks.")

        # ✅ Optional: Print a few previews for debugging
        for i, chunk in enumerate(chunks[:3]):
            print(f"🔹 Chunk {i + 1} preview:\n{chunk.page_content[:300]}...\n")

        return chunks

    except Exception as e:
        print(f"❌ Error in load_and_split_pdf: {e}")
        return []

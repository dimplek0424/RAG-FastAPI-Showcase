from langchain.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
import hashlib

# Custom modules for PDF parsing and RAG pipeline
from utils import load_and_split_pdf
from rag_engine import get_vectorstore_from_chunks, create_rag_chain

# Initialize the FastAPI app
app = FastAPI()

# CORS middleware to allow frontend apps (e.g. React) to access the backend APIs
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ In production, restrict to frontend URL (e.g., http://localhost:3000)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Verify OpenAI API key and connection on app startup
@app.on_event("startup")
async def verify_openai_key():
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("❌ OPENAI_API_KEY is not set in environment.")
            return
        from langchain_openai import OpenAIEmbeddings
        OpenAIEmbeddings(openai_api_key=api_key)  # Basic instantiation to test key
        print("✅ OPENAI_API_KEY is valid and OpenAI is reachable.")
    except Exception as e:
        print(f"❌ Issue verifying OpenAI key: {e}")

def generate_file_hash(file_path: str) -> str:
    """Generates a SHA-256 hash for a given file path."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

# Route: Upload and process a PDF file
@app.post("/upload/")
async def upload_pdf(file: UploadFile):
    """
    Endpoint to handle PDF uploads. It:
    - Saves the uploaded file locally
    - Splits it into chunks using LangChain
    - Creates embeddings and a vector store
    - Initializes a QA chain for RAG-style answering
    """
    try:
        os.makedirs("temp_files", exist_ok=True)

        file_path = f"temp_files/{file.filename}"
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        print(f"✅ Saved file to {file_path}")

        # Step 1: Load and split PDF into text chunks
        chunks = load_and_split_pdf(file_path)
        print(f"✅ Document split into {len(chunks)} chunks")

        if not chunks:
            return JSONResponse(status_code=400, content={"error": "PDF could not be processed or was empty."})

        # Step 2: Generate hash to identify this file for caching
        file_hash = generate_file_hash(file_path)
        vectorstore_path = os.path.join("vector_cache", f"{file_hash}_chroma")
        os.makedirs("vector_cache", exist_ok=True)

        embedding = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))

        # Step 3: Check if vectorstore cache exists
        if os.path.exists(vectorstore_path):
            print(f"🔄 Reusing vectorstore from cache for hash: {file_hash}")
            vectorstore = Chroma(persist_directory=vectorstore_path, embedding_function=embedding)
        else:
            print("📥 No cache found, generating new vectorstore...")
            vectorstore = Chroma.from_documents(chunks, embedding=embedding, persist_directory=vectorstore_path)
            vectorstore.persist()
            print("✅ New vectorstore created and cached")

        # Step 4: Build the RAG pipeline
        qa_chain = create_rag_chain(vectorstore)
        print("✅ QA chain initialized")

        # Initialize cache dictionary if not already present
        if not hasattr(app.state, "qa_chains"):
            app.state.qa_chains = {}

        # Cache the chain using file hash
        app.state.qa_chains[file_hash] = qa_chain
        app.state.active_chain_hash = file_hash  # Track current active chain

        return {"message": "PDF uploaded and indexed successfully."}

    except Exception as e:
        print(f"❌ Error during upload: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

# Route: Ask a question against uploaded PDF
@app.post("/ask/")
async def ask_question(question: str = Form(...)):
    """
    Endpoint to ask a natural language question.
    Returns an answer based on the uploaded PDF (RAG-based),
    along with the top source chunks used to generate it.
    """
    try:
        if not hasattr(app.state, "qa_chains") or not getattr(app.state, "active_chain_hash", None):
            return JSONResponse(
                status_code=400,
                content={"error": "No document uploaded yet. Please upload a PDF first."}
            )

        print(f"🧠 Question received: {question}")

        # Run the RAG chain
        qa_chain = app.state.qa_chains[app.state.active_chain_hash]
        result = qa_chain.invoke({"query": question})
        print("✅ Answer generated")

        # Extract the top source chunks (optional but helpful for debugging)
        answer = result['result']
        sources = [
            {"chunk": i + 1, "preview": doc.page_content[:300]}
            for i, doc in enumerate(result.get("source_documents", []))
        ]

        return {
            "answer": answer,
            "sources": sources
        }

    except Exception as e:
        print(f"❌ Error during QA: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

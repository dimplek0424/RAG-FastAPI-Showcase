from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi import HTTPException
import os
import shutil
import hashlib

# Custom modules for PDF parsing and RAG pipeline
from utils import load_and_split_pdf
from rag_engine import create_rag_chain, get_vectorstore_from_chunks

# Utility functions for maintenance tasks
from maintenance import delete_all_vectorstores, delete_vectorstore_by_hash, delete_temp_files

# Initialize the FastAPI app
app = FastAPI()

class QuestionInput(BaseModel):
    question: str

FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")

# ✅ Health check endpoint (used by Render or other platforms)
@app.get("/healthz")
def health_check():
    return {"status": "ok"}

# CORS middleware to allow frontend apps (e.g. React) to access the backend APIs
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],  # ✅ Replace this with your actual deployed frontend URL
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
        # ✅ Validate MIME type and file extension
        if file.content_type != "application/pdf" or not file.filename.lower().endswith(".pdf"):
            return JSONResponse(status_code=400, content={"error": "Only PDF files are allowed."})

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

        return {"message": "PDF uploaded and indexed successfully.",
                "file_hash": file_hash  # ✅ Add this line for easy testing
                }

    except Exception as e:
        print(f"❌ Error during upload: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

# Route: Ask a question against uploaded PDF
@app.post("/ask/")
async def ask_question(data: QuestionInput):
    """
    Handles a user question by:
    - Reconstructing the vectorstore from the cached directory
    - Rebuilding the RAG QA chain
    - Passing the user's question to the chain
    - Returning the AI-generated answer and top source chunks

    This approach ensures the app works even if memory-based state (app.state.qa_chains) is lost due to Render restarts.
    """
    try:
        # ✅ Step 1: Retrieve the current document hash from state (used during upload)
        file_hash = getattr(app.state, "active_chain_hash", None)
        if not file_hash:
            return JSONResponse(
                status_code=400,
                content={"error": "No document uploaded yet. Please upload a PDF first."}
            )

        # ✅ Step 2: Construct the path to the cached vectorstore for this PDF
        vectorstore_path = os.path.join("vector_cache", f"{file_hash}_chroma")

        # ✅ Step 3: Reinitialize the embedding model with the OpenAI API key
        embedding = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))

        # ✅ Step 4: Reload the vectorstore from disk using the persisted embeddings
        vectorstore = Chroma(
            persist_directory=vectorstore_path,
            embedding_function=embedding
        )

        # ✅ Step 5: Rebuild the RAG chain from the loaded vectorstore
        qa_chain = create_rag_chain(vectorstore)

        print(f"🧠 Question received: {data.question}")

        # ✅ Step 6: Pass the question to the QA chain and generate an answer
        result = qa_chain.invoke({"query": data.question})

        # ✅ Step 7: Extract answer and source previews
        answer = result["result"]
        sources = [
            {"chunk": i + 1, "preview": doc.page_content[:300]}  # Limit to first 300 characters for UI
            for i, doc in enumerate(result.get("source_documents", []))
        ]

        return {
            "answer": answer,
            "sources": sources
        }

    except Exception as e:
        print(f"❌ Error during QA: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

# ---------------------------
# 🔧 Utility: Delete all vectorstores
# ---------------------------
@app.delete("/cache/clear/")
def clear_all_vectorstores():
    """
    Deletes the entire 'vector_cache' directory and all stored vectorstores.
    Useful for resetting the system in development or managing disk space.
    """
    if delete_all_vectorstores():
        return {"message": "All cached vectorstores deleted."}
    else:
        raise HTTPException(status_code=500, detail="Failed to delete cached vectorstores.")


# ---------------------------
# 🔧 Utility: Delete vectorstore for a specific PDF hash
# ---------------------------
@app.delete("/cache/{file_hash}")
def clear_specific_vectorstore(file_hash: str):
    """
    Deletes a specific vectorstore by its file hash.
    Helps clean up cached data for one specific document.
    """
    try:
        if delete_vectorstore_by_hash(file_hash):
            return {"message": f"✅ Vectorstore for hash {file_hash} deleted."}
        return JSONResponse(status_code=404, content={"error": f"No vectorstore found for hash: {file_hash}"})
    except Exception as e:
        print(f"❌ Error in clear_specific_vectorstore: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete the specified vectorstore.")


# ---------------------------
# 🔧 Utility: Clear temp PDF uploads
# ---------------------------
@app.delete("/temp/clear/")
def clear_temp_files():
    """
    Deletes all files inside the 'temp_files' directory.
    Use this to clean up uploaded PDFs that are no longer needed.
    """
    if delete_temp_files():
        return {"message": "✅ All temp files cleared."}
    return JSONResponse(status_code=404, content={"error": "Temp files directory not found."})

@app.get("/debug/vectorstore-path/{file_hash}")
def check_vectorstore_path(file_hash: str):
    path = os.path.join("vector_cache", f"{file_hash}_chroma")
    return {"exists": os.path.exists(path), "path": path}
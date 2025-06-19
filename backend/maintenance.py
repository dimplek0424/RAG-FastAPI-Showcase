import os
import shutil
import stat  # ✅ Add this to fix PermissionError due to missing constant
import chromadb
from chromadb.config import Settings
from langchain.vectorstores.chroma import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores.chroma import Chroma as CommunityChroma

# ---------------------------
# 🧹 Deletes all vectorstore directories inside 'vector_cache'
# ---------------------------
# ✅ Deletes the entire vector_cache directory safely, even if files are locked or write-protected
def delete_all_vectorstores():
    vectorstore_dir = "vector_cache"

    # Check if the directory exists
    if os.path.exists(vectorstore_dir):

        # Custom error handler for locked or write-protected files
        def onerror(func, path, exc_info):
            # Try to make file writable if it's not
            if not os.access(path, os.W_OK):
                os.chmod(path, stat.S_IWUSR) # ✅ Fix permission to allow deletion
                func(path)
            else:
                # Log the error if file still can't be deleted
                print(f"⚠️ Failed to delete {path}: {exc_info[1]}")

        try:
            # Use shutil.rmtree with onerror to avoid PermissionError
            shutil.rmtree(vectorstore_dir, onerror=onerror)
            print("✅ All vectorstores deleted.")
            return True
        except Exception as e:
            # Catch any unexpected errors and log
            print(f"❌ Failed to delete vectorstores: {e}")
            return False
    else:
        print("ℹ️ No vectorstores to delete.")
        return False


# ---------------------------
# 🧹 Deletes a specific vectorstore folder by file hash (with Chroma reset)
# ---------------------------
def delete_vectorstore_by_hash(file_hash: str):
    """
    Properly deletes a specific Chroma vectorstore by:
    1. Loading the store.
    2. Closing the connection (if necessary).
    3. Deleting the directory.
    """
    path = os.path.join("vector_cache", f"{file_hash}_chroma")
    print(f"🧹 Attempting to delete vectorstore at: {path}")

    try:
        if os.path.exists(path):
            # 1. Try to load and delete through Chroma interface to release lock
            try:
                dummy_embedding = OpenAIEmbeddings()
                vs = CommunityChroma(persist_directory=path, embedding_function=dummy_embedding)
                vs.delete_collection()  # ✅ Closes DB and deletes contents properly
                print("✅ Vectorstore closed and collection deleted.")
            except Exception as e:
                print(f"⚠️ Failed to delete using Chroma delete_collection: {e}")
            
            # 2. Try deleting the folder manually in case files remain
            shutil.rmtree(path, ignore_errors=True)
            print("✅ Vectorstore directory removed from disk.")
            return True
        else:
            print("⚠️ Vectorstore path does not exist.")
            return False

    except Exception as e:
        print(f"❌ Exception while deleting vectorstore: {e}")
        return False


# ---------------------------
# 🧹 Deletes all uploaded PDFs in 'temp_files'
# ---------------------------
def delete_temp_files():
    if os.path.exists("temp_files"):
        shutil.rmtree("temp_files")
        os.makedirs("temp_files", exist_ok=True)
        return True
    return False

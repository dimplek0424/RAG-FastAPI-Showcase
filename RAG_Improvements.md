# Improving RAG Response Accuracy

Applied the following strategies to improve Retrieval-Augmented Generation (RAG) responses:

## 1. Custom Text Chunking
Instead of relying on fixed-length chunking, we implemented intelligent chunking to break text by semantic boundaries. This helped retain context in chunks.

## 2. File Hashing & VectorStore Caching
Generated an MD5 hash for each uploaded file and store its corresponding vector database on disk. If a file is uploaded again, we skip reprocessing and load from cache.

## 3. QA Chain Caching
Each file’s QA chain is cached in memory and tied to its file hash, ensuring that previously uploaded documents do not get overwritten.

## 4. Session-Based Chat History
Chat logs are stored in app state and retrieved per session + file hash, allowing users to see previous interactions per document.

## 5. Accurate Answer Filtering
By adjusting `k` in retriever and applying `stuff` chain type, we optimized relevance filtering of document chunks.

## 6. Input Sanitization
The backend checks empty questions, reuploads, and gracefully returns appropriate messages or reuses cached data.

## 7. Error Handling
If no PDF is uploaded or the server encounters an error, the frontend displays helpful user messages.
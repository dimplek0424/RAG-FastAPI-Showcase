# 📚 RAG_FASTAPI – Retrieval-Augmented Generation Chat Assistant

A lightweight Retrieval-Augmented Generation (RAG) web application using **Python**, **FastAPI**, **LangChain**, **ChromaDB**, and **OpenAI GPT-4** for intelligent question-answering on uploaded PDF documents.

## 🔗 Try it live: [https://rag-fastapi.vercel.app](https://rag-fastapi.vercel.app)
> ✨ New: Frontend session persistence and PDF-specific chat memory now live!

---

## 🧱 Tech Stack

- **Backend**: FastAPI · LangChain · OpenAI · ChromaDB
- **Frontend**: Vite + React
- **Vector Store**: Chroma
- **Deployment**:
  - Backend: Railway (Docker)
  - Frontend: Vercel (Vite React)
- **Language Support**: Python 3.10

---

## 🚀 Features

- ✅ Upload PDF documents
- ✅ Extract and embed content using OpenAI Embeddings
- ✅ Store and retrieve vectors using ChromaDB
- ✅ Ask questions in a modern, chat-style interface
- ✅ PDF-specific chat memory per file hash
- ✅ Session persistence via browser sessionStorage
- ✅ Fully integrated, cloud-deployed RAG pipeline

---

## 📂 Project Structure

```
RAG_FASTAPI/
├── backend/
│   ├── main.py
│   ├── utils/
│   ├── temp_files/
│   ├── chroma/
│   ├── requirements.txt
│   └── runtime.txt
├── frontend/
│   ├── public/
│   ├── src/
│   ├── vite.config.js
│   └── ...
├── .gitignore
├── Dockerfile
└── README.md
```

---

## ⚙️ Backend Setup (Railway + Docker)

### 🔧 Local Development

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### 🚢 Deployment on Railway (Docker)

**Dockerfile (backend/Dockerfile):**
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY ./backend /app
RUN apt-get update && apt-get install -y build-essential cargo && \
    pip install --upgrade pip && \
    pip install -r requirements.txt
EXPOSE 10000
CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--port=10000"]
```

**runtime.txt**:
```
python-3.10.13
```

**Railway Project Settings:**
```
Root Directory: /backend
Dockerfile Path: ./Dockerfile
Environment Variable:
OPENAI_API_KEY=your-openai-key
```

**Example Backend URL**:
```
https://ragfastapi-production.up.railway.app
```

---

## 🌐 Frontend Setup (Vercel)

### 🛠 Local Development

```bash
cd frontend
npm install
npm run dev
```

`.env` file:
```
VITE_BACKEND_URL=http://localhost:8000
```

### 🚀 Deploy on Vercel

1. Push repo to GitHub
2. Visit [vercel.com](https://vercel.com) → New Project → Import repo
3. Set **Environment Variable**:
```
VITE_BACKEND_URL=https://ragfastapi-production.up.railway.app
```
4. Deploy 🎉

---

## 🔄 Connecting Frontend to Backend

In `App.jsx`:
```js
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

await axios.post(`${BACKEND_URL}/ask/`, {
  question: "...",
  file_hash: currentHash,
});
```

---

## 🧪 Example API Call

**POST** `/ask`
```json
{
  "question": "What is the paper about?",
  "file_hash": "abc123..."
}
```
Response:
```json
{
  "answer": "This paper discusses...",
  "source_documents": [...]
}
```

---

## 🧼 .gitignore Highlights

```bash
__pycache__/
*.pyc
.env
backend/chroma/
backend/temp_files/
```

---

## 🧠 Credits

Built with 💡 by [Dimple Khatri](https://github.com/dimplek0424)  
Uses: Python · LangChain · ChromaDB · FastAPI · Vercel · Railway

---

## 📎 License

MIT License


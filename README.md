# 📚 RAG_FASTAPI – Retrieval-Augmented Generation Chat Assistant

A lightweight Retrieval-Augmented Generation (RAG) web application using **FastAPI**, **LangChain**, **ChromaDB**, and **OpenAI GPT-4** for intelligent question-answering on uploaded PDF documents.

## 🧱 Tech Stack

- **Backend**: FastAPI · LangChain · OpenAI · ChromaDB
- **Frontend**: Vite + React
- **Vector Store**: Chroma
- **Deployment**:
  - Backend: Render (Docker)
  - Frontend: Vercel (Vite React)
- **Language Support**: Python 3.10

---

## 🚀 Features

- Upload PDF documents
- Extract and embed content using OpenAI Embeddings
- Store and retrieve vectors using ChromaDB
- Ask questions in a chat UI and get grounded responses via GPT
- Session-based chat persistence
- Live deployed frontend + backend integration

---

## 📂 Project Structure

```
RAG_FASTAPI/
├── backend/
│   ├── main.py
│   ├── utils/
│   ├── temp_files/
│   ├── chroma/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── runtime.txt
├── frontend/
│   ├── public/
│   ├── src/
│   ├── vite.config.js
│   └── ...
├── .gitignore
└── README.md
```

---

## ⚙️ Backend Setup (Render + Docker)

### 🔧 Local Development

1. **Install dependencies:**

```bash
cd backend
pip install -r requirements.txt
```

2. **Run the app:**

```bash
uvicorn main:app --reload
```

---

### 🚢 Deployment on Render (Docker)

1. **Dockerfile**

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

2. **runtime.txt** (in `backend/`):

```
python-3.10.13
```

3. **Render Settings**:
   - Name: `rag-fastapi-backend`
   - Branch: `main`
   - Root Directory: *(leave blank for Docker)*
   - Docker Build Context: `.`  
   - Dockerfile Path: `./Dockerfile`
   - Instance: Free or Starter
   - Environment Variable:
     ```
     OPENAI_API_KEY=your-key-here
     ```

4. **Render URL (example)**:
```
https://rag-fastapi-backend.onrender.com
```

---

## 🌐 Frontend Setup (Vercel)

### 🛠 Local Development

1. Install dependencies:

```bash
cd frontend
npm install
```

2. Run the frontend:

```bash
npm run dev
```

Make sure `.env` contains:
```
VITE_BACKEND_URL=http://localhost:8000
```

---

### 🚀 Deploy on Vercel

1. Push your repo to GitHub.
2. Go to [vercel.com](https://vercel.com) → New Project → Import your repo.
3. Set Environment Variable:

```
VITE_BACKEND_URL=https://rag-fastapi-backend.onrender.com
```

4. Click **Deploy**. Done!

---

## 🔄 Connecting Frontend to Backend

In your React code:

```js
const BASE_URL = import.meta.env.VITE_BACKEND_URL;

const response = await fetch(`${BASE_URL}/ask`, {
  method: "POST",
  body: JSON.stringify({ question: "..." }),
});
```

---

## 🧪 Example API Call

**POST** `/ask`

```json
{
  "question": "What is the paper about?",
  "chat_history": []
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

Make sure your `.gitignore` includes:

```
__pycache__/
*.pyc
.env
backend/chroma/
backend/temp_files/
```

---

## 🧠 Credits

Built with 💡 by [Dimple Khatri](https://github.com/dimplek0424)  
Uses: Python, LangChain, ChromaDB, FastAPI, Vercel, Render

---

## 📎 License

MIT License
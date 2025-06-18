# Deployment Guide

Instructions to run this full-stack RAG Chat Assistant locally and deploy if needed.

## 🧰 Requirements

- Node.js >= 16.x
- Python >= 3.9
- OpenAI API key

---

## 🔧 Backend Setup

```bash
cd backend
python -m venv venv
source venv/Scripts/activate  # Windows
# or
source venv/bin/activate      # macOS/Linux

pip install -r requirements.txt
```

### .env File

Create `.env` file inside `/backend/` with:

```ini
OPENAI_API_KEY=your_openai_key_here
```

### Start Backend

```bash
uvicorn main:app --reload
```

Visit: http://127.0.0.1:8000

---

## 💻 Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Visit: http://localhost:5173

---

## 📁 Project Structure

```
rag-chat-assistant/
├── backend/
│   ├── main.py
│   ├── utils.py
│   ├── rag_engine.py
│   └── requirements.txt
├── frontend/
│   ├── App.jsx
│   ├── App.css
│   └── index.html
├── docs/
│   ├── RAG_Improvements.md
│   ├── UX_Design_Notes.md
│   └── Deployment.md
└── README.md
```
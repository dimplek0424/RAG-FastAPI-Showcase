# RAG Chat Assistant (Local Setup Guide)

A full-stack Retrieval-Augmented Generation (RAG) assistant built using FastAPI (backend) and React (frontend).

---

## 🔧 Setup Instructions

### 1. Clone This Repository

```bash
git clone https://github.com/your-username/rag-chat-assistant.git
cd rag-chat-assistant
```

### 2. Setup Python Backend

```bash
cd backend
python -m venv venv
source venv/Scripts/activate  # On Windows
# or
source venv/bin/activate  # On macOS/Linux

pip install -r requirements.txt
```

### 3. Set OpenAI API Key

Create a `.env` file inside `/backend`:

```ini
OPENAI_API_KEY=your_openai_key_here
```

### 4. Run Backend

```bash
uvicorn main:app --reload
```

Navigate to: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

### 5. Setup Frontend

```bash
cd ../frontend
npm install
npm run dev
```

Navigate to: [http://localhost:5173](http://localhost:5173)

---

## 📁 Project Structure

```txt
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

---

## 📘 Documentation

- [🧠 How We Improved RAG Responses](docs/RAG_Improvements.md)
- [🎨 Frontend UX Decisions & Design Notes](docs/UX_Design_Notes.md)
- [🚀 Deployment Guide](docs/Deployment.md)
- [📄 How to Get Your OpenAI API Key](docs/How%20to%20get%20an%20OpenAI%20API%20key.pdf)

---

## 🧪 Sample Prompt

> “List all strategies mentioned in the uploaded document.”

The assistant will extract facts directly from the file and cite relevant chunks.

---

## 🙌 Acknowledgements

Built with ❤️ using:
- [LangChain](https://www.langchain.com/)
- [OpenAI GPT-4o](https://platform.openai.com/)
- [Chroma](https://www.trychroma.com/)
- [React](https://reactjs.org/)
- [FastAPI](https://fastapi.tiangolo.com/)

---

## 🔐 Disclaimer

You are responsible for securing and managing your OpenAI API key usage and credits.

import React, { useState } from "react";
import axios from "axios";
import SparkMD5 from "spark-md5";
import "./App.css"; // Custom styles

function App() {
  // === STATE VARIABLES ===
  const [pdfFile, setPdfFile] = useState(null); // Stores the uploaded file
  const [pdfName, setPdfName] = useState(""); // Displayed filename
  const [fileHash, setFileHash] = useState(""); // Used for identifying cached chat

  const [uploadSuccess, setUploadSuccess] = useState(false); // To show/hide chat section
  const [isUploading, setIsUploading] = useState(false); // Show processing spinner
  const [isThinking, setIsThinking] = useState(false); // Show bot is generating answer

  const [question, setQuestion] = useState(""); // Current input question
  const [chatLog, setChatLog] = useState([]); // Current chat log for this file
  const [chatCache, setChatCache] = useState({}); // Stores all chats per fileHash
  const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

  // === FILE SELECTION ===
  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Compute hash to identify document uniquely
    const reader = new FileReader();
    reader.onload = (e) => {
      const hash = SparkMD5.hashBinary(e.target.result);
      setFileHash(hash);
      setChatLog(chatCache[hash] || []); // Restore cached chat if available
    };
    reader.readAsBinaryString(file);

    setPdfFile(file);
    setPdfName(file.name);
  };

  // === UPLOAD FILE TO BACKEND ===
  const handleUpload = async () => {
    if (!pdfFile) return;
    const formData = new FormData();
    formData.append("file", pdfFile);

    try {
      setIsUploading(true);
      await axios.post("${BACKEND_URL}/upload/", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setUploadSuccess(true);
      setChatLog([]);
    } catch (err) {
      console.error("Upload failed:", err);
    } finally {
      setIsUploading(false);
    }
  };

  // === ASK QUESTION ===
  const handleAsk = async () => {
    if (!question.trim()) return;
    setIsThinking(true);

    try {
      const response = await axios.post(
        "${BACKEND_URL}/ask/",
        new URLSearchParams({ question }),
        { headers: { "Content-Type": "application/x-www-form-urlencoded" } }
      );

      const answer = response.data.answer.replace(/\n/g, "<br/>");
      const updatedChat = [
        ...chatLog,
        { type: "user", text: question },
        { type: "bot", text: answer },
      ];

      setChatLog(updatedChat);
      setChatCache((prev) => ({ ...prev, [fileHash]: updatedChat }));
      setQuestion("");
    } catch (err) {
      console.error("Question error:", err);
    }

    setIsThinking(false);
  };

  // === RESET STATE ===
  const handleClear = () => {
    setPdfFile(null);
    setPdfName("");
    setUploadSuccess(false);
    setChatLog([]);
    setQuestion("");
    setFileHash("");
  };

  // === RENDER UI ===
  return (
    <div className="app-container">
      <h2>📄 RAG Chat Assistant</h2>
      {pdfName && <p className="filename-display">📎 {pdfName}</p>}

      <div className="upload-wrapper">
        <input
          type="file"
          id="pdf-upload"
          accept=".pdf"
          onChange={handleFileChange}
          hidden
          disabled={uploadSuccess} // Prevent selecting new file after upload
        />
        <label htmlFor="pdf-upload" className="upload-label">
          📎 Choose PDF
        </label>
        <button
          className={`upload-button ${!pdfFile ? "disabled" : ""}`}
          onClick={handleUpload}
          disabled={!pdfFile || uploadSuccess} // Prevent re-upload
        >
          Upload PDF
        </button>
        <button onClick={handleClear} className="clear-button">
          Clear
        </button>
      </div>

      {isUploading && <p className="uploading-msg">⏳ Processing your PDF...</p>}

      {uploadSuccess && (
        <div className="chatbox">
          {chatLog.map((msg, idx) => (
            <div key={idx} className={`chat-bubble ${msg.type}`}>
              <span dangerouslySetInnerHTML={{ __html: msg.text }} />
            </div>
          ))}

          {isThinking && (
            <div className="chat-bubble bot thinking">
              <span>💬 Thinking...</span>
            </div>
          )}

          <div className="chat-input">
            <input
              type="text"
              value={question}
              placeholder="Ask a question about the document..."
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && !isThinking && handleAsk()}
              disabled={isThinking} // Prevent sending while processing
            />
            <button onClick={handleAsk} disabled={isThinking || !question.trim()}>
              Send
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
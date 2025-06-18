# Frontend UX Design Notes

Our focus was to make the document Q&A experience seamless and interactive.

## 🎨 UI Improvements

- Fully centered layout on all screen sizes using Flexbox.
- Visual feedback when uploading files (`Uploading...` spinner).
- Display of uploaded filename below the title.
- Different chat bubble styles for user and bot messages.

## 🧠 Intelligent Behavior

- Disable the "Upload" button after a document is uploaded.
- Prevent sending new questions while AI is responding.
- Allow editing a question during "thinking" phase but disable "Send" until response returns.
- Only show chatbox after a successful PDF upload.

## 📱 Mobile Responsive

- Upload and chat input sections stack vertically on small screens.
- Font and button sizes remain accessible and readable.

## 🛠 Reusability

- Reusable state hooks and event handlers.
- Clean JSX with class-based styling via `App.css`.
- Added helpful inline comments in `App.jsx` and `App.css`.
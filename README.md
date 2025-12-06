# Modern Voice Chatbot

An end-to-end Agentic AI Voice Chatbot built with the most advanced frameworks. This application features a voice-first interface where users can speak to an intelligent agent that maintains conversation history and context.

## 🚀 Features

-   **Voice Interaction:** Real-time Speech-to-Text (STT) and Text-to-Speech (TTS) using OpenAI's best models (Whisper & TTS-1-HD).
-   **Agentic AI:** Powered by **LangGraph**, the agent understands context, manages tasks, and decides when to search memory.
-   **Long-term Memory:** Utilizes **Milvus** (Vector Database) to store and retrieve chat history, allowing the agent to answer follow-up questions effectively.
-   **Modern UI:** Built with **React**, **Vite**, and **Tailwind CSS** for a sleek, responsive experience.
-   **Scalable Backend:** **FastAPI** drives the backend services, ensuring high performance and easy extensibility.

## 🛠️ Tech Stack

### Backend
-   **Language:** Python 3.12+
-   **Framework:** FastAPI
-   **AI Orchestration:** LangGraph (LangChain ecosystem)
-   **LLM:** GPT-4o (via OpenAI)
-   **Vector DB:** Milvus (using `milvus-lite` for local development)
-   **Audio:** OpenAI Whisper (STT) & OpenAI TTS

### Frontend
-   **Framework:** React 19 (via Vite)
-   **Styling:** Tailwind CSS v3
-   **Icons:** Lucide React
-   **HTTP Client:** Axios

## 📋 Prerequisites

-   Python 3.12 or higher
-   Node.js 18 or higher
-   OpenAI API Key

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd modern-voice-chatbot
```

### 2. Backend Setup
Navigate to the backend directory and install dependencies:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Frontend Setup
Navigate to the frontend directory and install dependencies:
```bash
cd frontend
npm install
```

## 🚀 Running the Application

### 1. Start the Backend
You need to set your OpenAI API Key.
```bash
cd backend
export OPENAI_API_KEY="your-sk-..."
python3 -m uvicorn backend.app.main:app --reload --port 8000
```
The backend will run on `http://localhost:8000`.

### 2. Start the Frontend
In a new terminal:
```bash
cd frontend
npm run dev
```
The frontend will typically run on `http://localhost:5173`.

## 🧠 Architecture Overview

1.  **User speaks** into the frontend interface.
2.  Audio is sent to the **FastAPI backend**.
3.  **OpenAI Whisper** transcribes the audio to text.
4.  The text is passed to the **LangGraph Agent**.
5.  The Agent:
    -   Searches **Milvus** for relevant past context.
    -   Decides on the best response using **GPT-4o**.
    -   Saves the new interaction to Milvus.
6.  The response text is converted to audio using **OpenAI TTS**.
7.  Audio and text are sent back to the frontend for playback and display.

## 📂 Directory Structure

```
.
├── backend/
│   ├── app/
│   │   ├── agents/      # LangGraph agent logic
│   │   ├── services/    # OpenAI and Memory services
│   │   └── main.py      # FastAPI entry point
│   ├── requirements.txt
│   └── ...
├── frontend/
│   ├── src/
│   │   ├── components/  # React components (ChatInterface)
│   │   ├── hooks/       # Custom hooks (useChat)
│   │   └── ...
│   ├── package.json
│   └── ...
└── README.md
```

## 🧪 Verification / Dry Run

The repository includes a `dryrun_outputs/` directory containing screenshots from the automated verification process, demonstrating the application's functionality.

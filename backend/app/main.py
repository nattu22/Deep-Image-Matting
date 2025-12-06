from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from backend.app.services.openai_service import openai_service
from backend.app.agents.chat_agent import chat_agent
import uuid
import io

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextChatRequest(BaseModel):
    session_id: str
    message: str

class TextChatResponse(BaseModel):
    response: str
    audio_url: str = None # Client can request audio separately or we stream it

@app.get("/")
def read_root():
    return {"message": "Modern Voice Chatbot Backend is running"}

@app.post("/chat/audio")
async def chat_audio(
    file: UploadFile = File(...),
    session_id: str = Form(...)
):
    try:
        # 1. Transcribe
        text_input = await openai_service.transcript_audio(file)

        # 2. Get Agent Response
        response_text = await chat_agent.get_response(session_id, text_input)

        # 3. Convert Response to Audio
        audio_io = await openai_service.text_to_speech(response_text)

        # Return audio directly.
        # Ideally, we might want to return JSON with text AND audio,
        # but returning audio stream is easiest for voice-first apps.
        # However, to update the UI text, we should probably return both.
        # But StreamingResponse is for binary.
        # Let's return the audio and put the text in a header or
        # expecting the client to handle it.
        # Better: Return JSON with base64 audio or a separate ID.
        # Simple approach for now: Return audio, put text in custom header.

        headers = {"X-Response-Text": response_text.encode('utf-8').decode('latin-1')}
        # Encoding header value carefully or just base64 it if complex chars

        return StreamingResponse(audio_io, media_type="audio/mpeg", headers={"X-Chat-Response": response_text})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/text")
async def chat_text(request: TextChatRequest):
    try:
        response_text = await chat_agent.get_response(request.session_id, request.message)
        # We can also generate audio if requested, but let's stick to text-in-text-out for this endpoint
        return {"response": response_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tts")
async def tts(text: str = Form(...)):
    audio_io = await openai_service.text_to_speech(text)
    return StreamingResponse(audio_io, media_type="audio/mpeg")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

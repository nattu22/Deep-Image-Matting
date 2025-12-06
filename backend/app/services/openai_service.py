import os
from openai import OpenAI
from fastapi import UploadFile
import io

class OpenAIService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            self.client = OpenAI(api_key=api_key)
        else:
            self.client = None
            print("Warning: OpenAI Client not initialized (missing API Key)")

    async def transcript_audio(self, file: UploadFile) -> str:
        """
        Transcribes audio using OpenAI Whisper.
        """
        if not self.client or os.getenv("OPENAI_API_KEY") == "sk-dummy-key":
             return "This is a mock transcription."

        # Read file content
        content = await file.read()
        # Create a file-like object
        audio_file = io.BytesIO(content)
        audio_file.name = "audio.wav"  # Whisper requires a filename/extension

        transcription = self.client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
        return transcription.text

    async def text_to_speech(self, text: str) -> io.BytesIO:
        """
        Converts text to speech using OpenAI TTS.
        """
        if not self.client or os.getenv("OPENAI_API_KEY") == "sk-dummy-key":
             # Return a dummy wav file or empty bytes
             # Let's create a minimal valid wav header if possible, or just empty
             return io.BytesIO(b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00")

        response = self.client.audio.speech.create(
            model="tts-1-hd",
            voice="alloy",
            input=text
        )

        # Return audio stream
        return io.BytesIO(response.content)

openai_service = OpenAIService()

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from agent import FinancialSafetyNet
import shutil
import os
import json

app = FastAPI()

# Enable CORS for React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static directory for audio files
os.makedirs("static/audio", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize Agent
try:
    agent = FinancialSafetyNet()
except Exception as e:
    print(f"Failed to initialize agent: {e}")
    agent = None

@app.post("/analyze")
async def analyze(
    text: str = Form(None),
    type: str = Form("unknown"),
    file: UploadFile = File(None)
):
    if not agent:
        raise HTTPException(status_code=500, detail="Agent not initialized. Check API Key.")

    file_path = None
    image_path = None
    audio_path = None

    if file:
        # Save uploaded file temporarily
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Determine if it's image or audio based on extension or type hint
        if file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            image_path = file_path
        elif file.filename.lower().endswith(('.mp3', '.wav', '.m4a', '.ogg')):
            audio_path = file_path
        elif type == "upi_qr": # Fallback if extension is missing but type is known
            image_path = file_path

    try:
        result = agent.analyze(text_input=text, image_path=image_path, audio_path=audio_path, category_hint=type)
        
        # Cleanup uploaded file
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            
        return result
    except Exception as e:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"status": "Financial Safety Net API is running"}

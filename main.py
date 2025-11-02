import json
import requests
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import os

# 1️⃣ Load environment variables
load_dotenv()

# 2️⃣ Get values from .env (with default fallbacks)
MODEL_NAME = os.getenv("MODEL_NAME", "llama3")
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://127.0.0.1:11434/api/generate")

# 3️⃣ Initialize FastAPI app
app = FastAPI(title="AI Agent Backend (Ollama Streaming)")

# 4️⃣ Enable CORS (for frontend connection)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify ["http://localhost:4200"] for your Angular app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5️⃣ Request body model
class ChatRequest(BaseModel):
    message: str
    user_id: int

# 6️⃣ Root route
@app.get("/")
def home():
    return {
        "message": "✅ AI Agent Backend is running!",
        "model": MODEL_NAME,
        "ollama_url": OLLAMA_API_URL,
    }

# 7️⃣ AI query route
@app.post("/api/ai/query")
async def query_ai(request: Request):
    data = await request.json()
    user_message = data.get("message", "")

    def generate():
        try:
            with requests.post(
                OLLAMA_API_URL,
                json={"model": MODEL_NAME, "prompt": user_message},
                stream=True
            ) as r:
                for line in r.iter_lines():
                    if line:
                        json_data = json.loads(line.decode("utf-8"))
                        chunk = json_data.get("response", "")
                        if chunk:
                            yield f"data: {chunk}\n\n"
                yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: [ERROR] {str(e)}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")

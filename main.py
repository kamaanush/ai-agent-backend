import json
import requests
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
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
    allow_origins=["*"],  # Change to ["http://localhost:4200"] if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5️⃣ Request body model
class ChatRequest(BaseModel):
    message: str
    user_id: int


# 6️⃣ API route: backend health check
@app.get("/api")
def home():
    return {
        "message": "✅ AI Agent Backend is running!",
        "model": MODEL_NAME,
        "ollama_url": OLLAMA_API_URL,
    }


# 7️⃣ API route: AI Query
@app.post("/api/ai/query")
async def query_ai(request: Request):
    data = await request.json()
    user_message = data.get("message", "")

    def generate():
        try:
            with requests.post(
                OLLAMA_API_URL,
                json={"model": MODEL_NAME, "prompt": user_message},
                stream=True,
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


# 8️⃣ Default route to avoid 404 on root
@app.get("/")
def root():
    return {"message": "Backend is running successfully 🚀"}


# 9️⃣ Serve Angular Frontend (Production Build)
frontend_path = os.path.join(os.path.dirname(__file__), "../frontend/dist/ai-agent-frontend")

if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

    @app.get("/")
    async def serve_index():
        return FileResponse(os.path.join(frontend_path, "index.html"))

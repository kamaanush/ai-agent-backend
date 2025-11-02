import json
import requests
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

app = FastAPI(title="AI Agent Backend (Ollama Streaming)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    user_id: int

# ✅ Add home route to prevent 404
@app.get("/")
def home():
    return {"message": "✅ AI Agent Backend is running!"}

OLLAMA_API_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "llama3"

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

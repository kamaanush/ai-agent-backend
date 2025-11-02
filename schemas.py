from pydantic import BaseModel

class ChatHistoryBase(BaseModel):
    user_message: str
    ai_reply: str

    class Config:
        orm_mode = True

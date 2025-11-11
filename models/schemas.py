from pydantic import BaseModel

class ChatRequest(BaseModel):
    query: str
    file_id: str

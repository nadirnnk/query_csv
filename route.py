from fastapi import APIRouter, UploadFile, File
from models.schemas import ChatRequest
import calls, data
from utils.sand import execute_code


upload = APIRouter(prefix="/upload", tags=["Upload"])

@upload.post("/")
async def upload_csv(file: UploadFile = File(...)):
    file_id = await data.save_csv(file)
    return {"message": "File uploaded successfully", "file_id": file_id}



chat = APIRouter(prefix="/chat", tags=["Chat"])

@chat.post("/")
async def chat_with_csv(request: ChatRequest):
    df = data.get_csv(request.file_id)
    code = await calls.generate_pandas_code(request.query, df)
    print("Generated Code:", code)
    output = execute_code(code, df)
    return {"generated_code": code, "result": output["result"], "image": output["image"], "error": output["error"]}
from fastapi import APIRouter, UploadFile, File
from models.schemas import ChatRequest, FeedbackRequest
import data
import calls
from calls import code_gen
from utils.sand import execute_code
from prompt import prompt
import uuid


class CSVChatAPI:
    def __init__(self):
        # Routers
        self.upload = APIRouter(prefix="/upload", tags=["Upload"])
        self.chat = APIRouter(prefix="/chat", tags=["Chat"])


        # Route bindings
        self.upload.post("/")(self.upload_csv)
        self.chat.post("/")(self.chat_with_csv)
        self.chat.get("/history/{user_id}")(self.get_chat_history)
        self.chat.post("/feedback")(self.submit_feedback)
       

    # =====================================================
    # 📂 Upload CSV
    # =====================================================
    async def upload_csv(self, file: UploadFile = File(...)):
        file_id = await data.save_csv(file)
        return {"message": "File uploaded successfully", "file_id": file_id}

    # =====================================================
    # 💬 Chat Endpoint
    # =====================================================
    async def chat_with_csv(self, request: ChatRequest):
        df = data.get_csv(request.file_id)
        bot = code_gen(user_id=request.user_id)

        code, user_id = await bot.generate_code(request.query, df)
        output = execute_code(code, df)

        return {
            "generated_code": code,
            "result": output.get("result"),
            "image": output.get("image"),
            "error": output.get("error"),
            "user_id": user_id,
        }

    # =====================================================
    # 🧠 Get Chat History
    # =====================================================
    async def get_chat_history(self, user_id: str):
        """
        Returns the chat history for a specific user_id.
        """
        history, user_id = calls.get_user_history(user_id)
        return {"user_id": user_id, "history": history}

    # =====================================================
    # 👍 Submit Feedback
    # =====================================================
    async def submit_feedback(self, request: FeedbackRequest):
        """
        Store thumbs up/down feedback for the last query/result pair.
        feedback can be: 'thumbs_up', 'thumbs_down', or None
        """
        print(f"[FEEDBACK] Received feedback from user {request.query}: {request.code}, {request.feedback}")
        calls.add_feedback(request.query, request.code, request.feedback)
        return {"message": "Feedback received", "feedback": request.feedback}



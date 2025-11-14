from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from route import CSVChatAPI

app = FastAPI(title="AI CSV Analyzer API")

# Allow Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or specific domain later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api = CSVChatAPI()
app.include_router(api.upload)
app.include_router(api.chat)
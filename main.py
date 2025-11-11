from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from route import chat, upload

app = FastAPI(title="AI CSV Analyzer API")

# Allow Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or specific domain later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat)
app.include_router(upload)

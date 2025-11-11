import pandas as pd
import uuid
import os

UPLOAD_DIR = "storage/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
_cache = {}

async def save_csv(file):
    file_id = str(uuid.uuid4())
    filepath = os.path.join(UPLOAD_DIR, f"{file_id}.csv")
    with open(filepath, "wb") as f:
        f.write(await file.read())
    df = pd.read_csv(filepath)
    _cache[file_id] = df
    return file_id

def get_csv(file_id):
    return _cache.get(file_id)

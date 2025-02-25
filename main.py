import os
import uuid
from fastapi import FastAPI, File, UploadFile, HTTPException, status
from fastapi.responses import JSONResponse, FileResponse
import redis
from pydantic import BaseModel

app = FastAPI()

redis_client = redis.Redis(host='redis', port=6379, db=0)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class Task(BaseModel):
    title: str
    file_path: str

@app.get("/status", status_code=status.HTTP_200_OK)
async def status_work():
    return {"status": "working"}

@app.post("/task", status_code=status.HTTP_201_CREATED)
async def create_task(image: UploadFile = File(...), title: str = "") -> JSONResponse:
    if image.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ошибка валидации: некорректный MIME-тип")

    task_id = str(uuid.uuid4())

    file_path = os.path.join(UPLOAD_DIR, f"{task_id}.{image.filename.split('.')[-1]}")
    with open(file_path, "wb") as buffer:
        buffer.write(await image.read())

    task_data = Task(title=title, file_path=file_path)
    redis_client.set(task_id, task_data.model_dump_json())

    return JSONResponse(content={"task_id": task_id, "status": "saved"})

@app.get("/task/{task_id}", status_code=status.HTTP_200_OK)
async def get_task(task_id: str) -> FileResponse:
    task_data = redis_client.get(task_id)
    if not task_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    task = Task.model_validate_json(task_data)
    return FileResponse(task.file_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

from fastapi import APIRouter, status, UploadFile, File, Form, Depends
from typing import List
from backend.app.services.upload_service import UploadService
from backend.app.schemas.video import VideoResponse
from backend.app.core.config import settings
from supabase import create_client

router = APIRouter(prefix="/videos", tags=["Videos"])

supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
upload_service = UploadService(supabase_client)

@router.post("/upload", status_code=status.HTTP_201_CREATED, response_model=VideoResponse)
async def upload_video(
    file: UploadFile = File(...),
    title: str = Form(...),
    user_id: str = Form(...)
):
    return await upload_service.upload_video(file, title, user_id)

@router.get("/", response_model=List[VideoResponse])
async def get_all_videos():
    return await upload_service.get_all_videos()

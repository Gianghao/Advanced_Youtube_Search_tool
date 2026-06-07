from fastapi import APIRouter, status, UploadFile, File, Form, BackgroundTasks
from typing import List
from backend.app.services.upload_service import UploadService
from backend.app.schemas.video import VideoResponse
from backend.app.core.config import settings
from backend.pipeline.ai_pipeline import run_pipeline
from supabase import create_client

router = APIRouter(prefix="/videos", tags=["Videos"])

supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
upload_service = UploadService(supabase_client)


@router.post("/upload", status_code=status.HTTP_201_CREATED, response_model=VideoResponse)
async def upload_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str = Form(...),
    user_id: str = Form(...),
):
    """
    Upload video to Supabase Storage and activate AI pipeline.
    
    Pipeline will:
    1. Detect scenes by PySceneDetect
    2. Extract frame for each scene
    3. Encode frame by CLIP to 512-dim vector
    4. Save vector to Supabase pgvector
    
    Video status will: uploaded → processing → ready
    """
    # Upload video to Supabase Storage (status = "processing")
    video_data = await upload_service.upload_video(file, title, user_id)

    # Activate AI pipeline
    background_tasks.add_task(
        run_pipeline,
        video_id=video_data["video_id"],
        video_url=video_data["video_url"],
        title=video_data["title"],
        supabase_client=supabase_client,
        supabase_db_url=settings.SUPABASE_DB_URL,
        frames_bucket=settings.SUPABASE_FRAMES_BUCKET,
    )

    return video_data


@router.get("/", response_model=List[VideoResponse])
async def get_all_videos():
    """Get all videos (newest first)."""
    return await upload_service.get_all_videos()

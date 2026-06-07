from supabase import Client
from fastapi import UploadFile, HTTPException, status
import uuid
from datetime import datetime
from backend.app.core.config import settings

class UploadService:
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client

    async def upload_video(self, file: UploadFile, title: str, user_id: str):
        try:
            # Generate a unique ID for the video
            video_id = str(uuid.uuid4())
            file_extension = file.filename.split('.')[-1]
            file_path = f"{user_id}/{video_id}.{file_extension}"

            # Read file content
            file_content = await file.read()

            # Upload to Supabase Storage
            self.supabase.storage.from_(settings.SUPABASE_VIDEO_BUCKET).upload(
                path=file_path,
                file=file_content,
                file_options={"content-type": file.content_type}
            )

            # Get public URL
            public_url = self.supabase.storage.from_(settings.SUPABASE_VIDEO_BUCKET).get_public_url(file_path)

            # Insert record into videos table
            video_data = {
                "video_id": video_id,
                "title": title,
                "video_url": public_url,
                "status": "processing",
                "user_id": user_id,
                "timestamp": datetime.now().isoformat()
            }
            
            self.supabase.table("videos").insert(video_data).execute()

            return video_data
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    async def get_all_videos(self):
        try:
            response = self.supabase.table("videos").select("*").order("timestamp", desc=True).execute()
            return response.data
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

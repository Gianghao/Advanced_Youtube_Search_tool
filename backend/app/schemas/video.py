from pydantic import BaseModel
from datetime import datetime

class VideoResponse(BaseModel):
    video_id: str
    title: str
    video_url: str
    status: str
    user_id: str
    timestamp: datetime

class UploadVideo(BaseModel):
    user_id: str
    title: str
    
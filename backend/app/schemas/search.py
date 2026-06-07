from pydantic import BaseModel


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


class SearchResult(BaseModel):
    video_id: str
    title: str
    video_url: str
    timestamp_seconds: float
    frame_url: str
    similarity: float

    @property
    def timestamp_display(self) -> str:
        """Trả về timestamp dạng MM:SS."""
        total_sec = int(self.timestamp_seconds)
        minutes = total_sec // 60
        seconds = total_sec % 60
        return f"{minutes:02d}:{seconds:02d}"

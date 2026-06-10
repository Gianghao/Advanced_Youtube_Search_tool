from fastapi import APIRouter, HTTPException, status
from typing import List

from backend.app.schemas.search import SearchRequest, SearchResult
from backend.app.schemas.search import VideoSearchRequest, VideoSearchResult
from backend.app.services.search_service import SearchService
from backend.app.core.config import settings
from supabase import create_client

router = APIRouter(prefix="/search", tags=["Search"])

supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
search_service = SearchService(supabase_client, settings.SUPABASE_DB_URL)


@router.post("/", response_model=List[SearchResult])
async def search_videos(request: SearchRequest):
    """
    Search video content by query text.
    
    - **query**: Description of the content you want to find (e.g., "people walking on the street")
    - **top_k**: Number of results to return (default 5, max 20)
    
    Returns a list of results with video name, timestamp, and frame image link.
    Click the result to stream video from that timestamp.
    """
    if not request.query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query is required"
        )
    top_k = min(max(request.top_k, 1), 20)
    results = search_service.search(request.query, top_k)
    return results

@router.post("/title", response_model=List[VideoSearchResult])
async def search_video_by_title(request: VideoSearchRequest):
    """
    Search videos by title using simple SQL LIKE.
    
    - **query**: Text to search in video titles (e.g., "cat video")
    - **top_k**: Number of results to return (default 5, max 20)
    
    Returns a list of videos with title and URL.
    Click the result to watch the video.
    """
    if not request.query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query is required"
        )
    top_k = min(max(request.top_k, 1), 20)
    results = search_service.search_video_by_title(request.query, top_k)
    return results
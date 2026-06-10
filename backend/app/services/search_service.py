"""
Search Service
--------------
Encode query text bằng CLIP, tìm kiếm similarity trong vecs collection,
join với bảng videos để lấy thông tin video.
"""
import logging
from typing import Optional

import vecs
from supabase import Client

from backend.app.schemas.search import SearchResult
from backend.app.schemas.search import VideoSearchResult

logger = logging.getLogger(__name__)

# vecs client — lazy init, dùng chung
_vecs_client: Optional[vecs.Client] = None
_collection: Optional[vecs.Collection] = None


def get_collection(db_url: str) -> vecs.Collection:
    """Lấy hoặc tạo vecs collection (lazy init)."""
    global _vecs_client, _collection
    if _vecs_client is None:
        _vecs_client = vecs.create_client(db_url)
    if _collection is None:
        _collection = _vecs_client.get_or_create_collection(name="video_frames", dimension=512)
    return _collection


class SearchService:
    def __init__(self, supabase_client: Client, db_url: str):
        self.supabase = supabase_client
        self.db_url = db_url

    def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        """
        Encode query → vector → similarity search trong vecs → trả về top-k kết quả.
        Metadata đã được lưu kèm vector trong pipeline, bao gồm video_id, title, timestamp, frame_url, video_url.
        """
        # Import ở đây để tránh load model khi server start (chỉ load khi cần)
        from backend.pipeline.ai_pipeline import encode_text

        logger.info(f"[Search] Query: '{query}', top_k={top_k}")

        # Encode query text thành vector 512-dim
        query_vector = encode_text(query)

        # Lấy collection và query
        collection = get_collection(self.db_url)
        try:
            raw_results = collection.query(
                data=query_vector,
                limit=top_k,
                include_metadata=True,
                include_value=True,    # trả về similarity score
            )
        except Exception as e:
            logger.error(f"[Search] vecs query thất bại: {e}")
            return []

        results: list[SearchResult] = []
        for item in raw_results:
            # item là tuple: (id, distance, metadata) khi include_value=True
            # hoặc (id, metadata) khi chỉ include_metadata=True
            # vecs trả về cosine distance (0=giống nhau, 1=khác), similarity = 1 - distance
            if len(item) == 3:
                _frame_id, distance, metadata = item
                similarity = float(1.0 - distance)
            else:
                _frame_id, metadata = item
                similarity = 0.0

            if not metadata:
                continue

            results.append(SearchResult(
                video_id=metadata.get("video_id", ""),
                title=metadata.get("title", "Unknown"),
                video_url=metadata.get("video_url", ""),
                timestamp_seconds=float(metadata.get("timestamp_seconds", 0.0)),
                frame_url=metadata.get("frame_url", ""),
                similarity=similarity,
            ))

        logger.info(f"[Search] Trả về {len(results)} kết quả")
        return results
    
    def search_video_by_title(self, query: str, top_k: int = 5) -> list [VideoSearchResult]:
    
        logger.info(f"[Search] Title search: '{query}', top_k={top_k}")
        try:
            response = (
                self.supabase
                .table("videos")
                .select("video_id, title, video_url")  # was "id" — must match your actual column name
                .ilike("title", f"%{query}%")
                .limit(top_k)
                .execute()
            )
            results = [
                VideoSearchResult(
                    video_id=v.get("video_id", ""),
                    title=v.get("title", "Unknown"),
                    video_url=v.get("video_url", "")
                )
                for v in response.data
            ]
            logger.info(f"[Search] Found {len(results)} videos by title")
            return results
        except Exception as e:
            logger.error(f"[Search] Title search error: {e}")
            return [] 

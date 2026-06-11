from supabase import Client
from fastapi import HTTPException, status
from backend.app.core.config import settings

class DeleteService:
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client

    async def delete_video(self, video_id: str, user_id: str):
        """
        Delete a video completely:
        - Remove from 'videos' table
        - Delete the original video file from Supabase Storage (video bucket)
        - Delete all associated frame images from frames bucket
        - (Optional) Delete pgvector entries – implement if you have vecs client
        """
        try:
            # 1. Get video details and verify ownership
            result = self.supabase.table("videos") \
                .select("video_url, user_id") \
                .eq("video_id", video_id) \
                .execute()

            if not result.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Video not found"
                )

            video = result.data[0]
            if video["user_id"] != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to delete this video"
                )

            video_url = video["video_url"]

            # 2. Extract storage path from video_url
            # URL format: https://xxx.supabase.co/storage/v1/object/public/video-bucket/user123/uuid.mp4
            if "/public/" not in video_url:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid video URL format"
                )

            path_after_public = video_url.split("/public/")[1]  # "video-bucket/user123/uuid.mp4"
            # Remove bucket name to get the actual file path inside the bucket
            file_path = path_after_public.split("/", 1)[1]      # "user123/uuid.mp4"

            # 3. Delete original video file from video bucket
            self.supabase.storage \
                .from_(settings.SUPABASE_VIDEO_BUCKET) \
                .remove([file_path])

            # 4. Delete all associated frame images from frames bucket
            #    List all files under folder named video_id/
            frames_bucket = settings.SUPABASE_FRAMES_BUCKET
            try:
                frames_list = self.supabase.storage \
                    .from_(frames_bucket) \
                    .list(video_id)
                if frames_list:
                    frame_paths = [f"{video_id}/{f['name']}" for f in frames_list if 'name' in f]
                    self.supabase.storage \
                        .from_(frames_bucket) \
                        .remove(frame_paths)
            except Exception as e:
                # Log but don't fail the whole operation; frames may be missing
                print(f"Warning: could not delete frames: {e}")

            # 5. (Optional) Delete vectors from pgvector collection.
            #    If you use `vecs`, you can do:
            #    import vecs
            #    vx = vecs.create_client(settings.SUPABASE_DB_URL)
            #    collection = vx.get_collection("video_frames")
            #    collection.delete(metadata={"video_id": video_id})
            #    vx.disconnect()
            #    For now, we skip this step.

            # 6. Delete the record from the 'videos' table
            self.supabase.table("videos") \
                .delete() \
                .eq("video_id", video_id) \
                .execute()

            return {"message": "Video deleted successfully"}

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete video: {str(e)}"
            )
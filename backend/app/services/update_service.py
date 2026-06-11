from supabase import Client
from fastapi import HTTPException, status

class UpdateService:
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client

    async def update_video(self, video_id: str, new_title: str, user_id: str):
        """
        Update the title of a video.
        Checks that the video exists and belongs to the user.
        """
        try:
            # Verify ownership
            check = self.supabase.table("videos") \
                .select("video_id") \
                .eq("video_id", video_id) \
                .eq("user_id", user_id) \
                .execute()

            if not check.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Video not found or you do not have permission to update it"
                )

            # Update title
            self.supabase.table("videos") \
                .update({"title": new_title}) \
                .eq("video_id", video_id) \
                .execute()

            # Fetch and return the updated video
            updated = self.supabase.table("videos") \
                .select("*") \
                .eq("video_id", video_id) \
                .execute()

            return updated.data[0]

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update video: {str(e)}"
            )
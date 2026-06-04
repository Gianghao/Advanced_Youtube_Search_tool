from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

@patch("backend.app.api.routes.video_router.upload_service.supabase")
def test_upload_video_success(mock_supabase):
    # Mock storage upload
    mock_storage = MagicMock()
    mock_supabase.storage.from_.return_value = mock_storage
    mock_storage.upload.return_value = {"path": "test-user-id/mock-video-id.mp4"}
    mock_storage.get_public_url.return_value = "http://example.com/mock-video.mp4"
    
    # Mock table insert
    mock_table = MagicMock()
    mock_supabase.table.return_value = mock_table
    mock_table.insert.return_value.execute.return_value = MagicMock(data=[])

    # Test data
    file_content = b"fake video content"
    files = {"file": ("test.mp4", file_content, "video/mp4")}
    data = {"title": "Test Video Title", "user_id": "test-user-id"}

    response = client.post("/videos/upload", files=files, data=data)
    
    assert response.status_code == 201
    res_data = response.json()
    assert res_data["title"] == "Test Video Title"
    assert res_data["user_id"] == "test-user-id"
    assert res_data["video_url"] == "http://example.com/mock-video.mp4"
    assert res_data["status"] == "uploaded"
    assert "video_id" in res_data
    
    mock_storage.upload.assert_called_once()
    mock_storage.get_public_url.assert_called_once()
    mock_table.insert.assert_called_once()

@patch("backend.app.api.routes.video_router.upload_service.supabase")
def test_get_all_videos_success(mock_supabase):
    # Mock data returned from database
    mock_videos = [
        {
            "video_id": "video1",
            "title": "Title 1",
            "video_url": "http://example.com/1.mp4",
            "status": "uploaded",
            "user_id": "user1",
            "timestamp": "2026-06-04T12:00:00Z"
        },
        {
            "video_id": "video2",
            "title": "Title 2",
            "video_url": "http://example.com/2.mp4",
            "status": "uploaded",
            "user_id": "user2",
            "timestamp": "2026-06-04T11:00:00Z"
        }
    ]
    
    # Mock table select query
    mock_query_result = MagicMock()
    mock_query_result.data = mock_videos
    mock_supabase.table.return_value.select.return_value.order.return_value.execute.return_value = mock_query_result

    response = client.get("/videos/")
    assert response.status_code == 200
    assert response.json() == mock_videos

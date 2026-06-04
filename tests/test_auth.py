from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

@patch("backend.app.api.routes.auth_router.auth_service.supabase")
def test_signup_success(mock_supabase):
    # Mocking supabase client auth sign_up response
    mock_user = MagicMock()
    mock_user.id = "test-user-id"
    
    mock_response = MagicMock()
    mock_response.user = mock_user
    mock_supabase.auth.sign_up.return_value = mock_response

    # Test data
    signup_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpassword123"
    }

    response = client.post("/auth/signup", json=signup_data)
    assert response.status_code == 201
    assert response.json() == {"message": "Sign up success!", "user_id": "test-user-id"}
    mock_supabase.auth.sign_up.assert_called_once_with({
        "email": "testuser@example.com",
        "password": "testpassword123",
        "options": {
            "data": {
                "username": "testuser"
            }
        }
    })

@patch("backend.app.api.routes.auth_router.auth_service.supabase")
def test_signin_success(mock_supabase):
    # Mocking supabase client auth sign_in response
    mock_user = MagicMock()
    mock_user.id = "test-user-id"
    mock_user.email = "testuser@example.com"
    
    mock_session = MagicMock()
    mock_session.access_token = "mock-access-token"
    mock_session.refresh_token = "mock-refresh-token"
    
    mock_auth_response = MagicMock()
    mock_auth_response.user = mock_user
    mock_auth_response.session = mock_session
    
    mock_supabase.auth.sign_in_with_password.return_value = mock_auth_response

    # Mocking supabase table profile query
    mock_query_result = MagicMock()
    mock_query_result.data = {"username": "testuser"}
    
    mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_query_result

    # Test data
    signin_data = {
        "email": "testuser@example.com",
        "password": "testpassword123"
    }

    response = client.post("/auth/signin", json=signin_data)
    assert response.status_code == 200
    assert response.json() == {
        "access_token": "mock-access-token",
        "refresh_token": "mock-refresh-token",
        "user_id": "test-user-id",
        "email": "testuser@example.com",
        "username": "testuser"
    }

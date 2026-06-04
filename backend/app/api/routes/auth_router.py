from fastapi import APIRouter, status
from backend.app.schemas.user import UserSignUp, UserSignIn, AuthResponse
from backend.app.services.auth_service import AuthService
from backend.app.core.config import settings
from supabase import create_client

router = APIRouter(prefix="/auth", tags=["Authentication"])

supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
auth_service = AuthService(supabase_client)

@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserSignUp):
    return await auth_service.sign_up(user_data)

@router.post("/signin", response_model=AuthResponse)
async def signin(user_data: UserSignIn):
    return await auth_service.sign_in(user_data)
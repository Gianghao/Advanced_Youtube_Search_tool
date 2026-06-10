from supabase import Client
from backend.app.schemas.user import UserSignUp, UserSignIn, AuthResponse
from fastapi import HTTPException, status

class AuthService:
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client

    async def sign_up(self, user_data: UserSignUp):
        try:
            response = self.supabase.auth.sign_up({
                "email": user_data.email,
                "password": user_data.password,
                "options": {
                    "data": {
                        "username": user_data.username
                    }
                }
            })
            return {"message": "Sign up success!", "user_id": response.user.id}
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    async def sign_in(self, user_data: UserSignIn) -> AuthResponse:
        try:
            response = self.supabase.auth.sign_in_with_password({
                "email": user_data.email,
                "password": user_data.password
            })
            
            profile_query = self.supabase.table("profiles").select("username").eq("id", response.user.id).single().execute()
            username = profile_query.data.get("username", "User")

            return AuthResponse(
                access_token=response.session.access_token,
                refresh_token=response.session.refresh_token,
                user_id=response.user.id,
                email=response.user.email,
                username=username
            )
        except Exception as e:
            print(f"Login error: {str(e)}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Wrong credentials! Error: {str(e)}")
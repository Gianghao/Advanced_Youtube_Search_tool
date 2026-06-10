from fastapi import APIRouter, status, HTTPException
from backend.app.schemas.user import UserUpdateUsername, UserUpdatePassword
from backend.app.core.config import settings
from backend.crud.user import get_crud
from supabase import create_client

router = APIRouter(prefix="/user", tags=["User"])

supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
user_crud = get_crud(supabase_client)

@router.put("/username", status_code=status.HTTP_200_OK)
async def update_username(user_data: UserUpdateUsername):
    try:
        user_crud.update(user_data.user_id, {"username": user_data.new_username})
        return {"message": "Username updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.put("/password", status_code=status.HTTP_200_OK)
async def update_password(user_data: UserUpdatePassword):
    try:
        # First, try to sign in to verify the old password
        response = supabase_client.auth.sign_in_with_password({
            "email": user_data.email,
            "password": user_data.old_password
        })
        
        # If successful, the supabase_client now has an active session
        # We can now update the user's password
        update_resp = supabase_client.auth.update_user({
            "password": user_data.new_password
        })
        
        return {"message": "Password updated successfully"}
    except Exception as e:
        print(f"Update password error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not update password. Check old password.")

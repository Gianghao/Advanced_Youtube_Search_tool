from pydantic import BaseModel, EmailStr, Field

class UserSignUp(BaseModel):
    username: str = Field(..., min_length=3, max_length=20, description="Username must be between 3 and 20 characters")
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserSignIn(BaseModel):
    email: EmailStr
    password: str

class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    user_id: str
    email: str
    username: str

class UserUpdateUsername(BaseModel):
    user_id: str
    new_username: str = Field(..., min_length=3, max_length=20)

class UserUpdatePassword(BaseModel):
    email: EmailStr
    old_password: str
    new_password: str = Field(..., min_length=6)
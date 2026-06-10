from typing import Optional, Any
from supabase import Client
from backend.crud.base import BaseCRUD

class UserCRUD(BaseCRUD):
    """Simple CRUD helper for the `profiles` table in Supabase.

    Inherits from BaseCRUD for standard operations (get, get_all, create, update, remove).
    """
    def __init__(self, supabase_client: Client):
        super().__init__(supabase_client, table_name="profiles")

    def get_by_email(self, email: str) -> Optional[Any]:
        resp = self.supabase.table(self.table_name).select("*").eq("email", email).single().execute()
        return resp.data

    def get_by_username(self, username: str) -> Optional[Any]:
        resp = self.supabase.table(self.table_name).select("*").eq("username", username).single().execute()
        return resp.data

def get_crud(supabase_client: Client) -> UserCRUD:
    """Convenience factory to create a `UserCRUD` instance."""
    return UserCRUD(supabase_client)

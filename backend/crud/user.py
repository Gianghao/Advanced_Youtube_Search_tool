from typing import Optional, Any
from supabase import Client


class UserCRUD:
	"""Simple CRUD helper for the `profiles` table in Supabase.

	This class performs lightweight operations and returns the raw
	`response.data` object from the Supabase client. Consumers (services/
	routers) may raise HTTP exceptions or perform validation as needed.
	"""

	def __init__(self, supabase_client: Client):
		self.supabase = supabase_client

	def create_profile(self, user_id: str, username: str, email: Optional[str] = None) -> Any:
		payload = {"id": user_id, "username": username}
		if email:
			payload["email"] = email
		resp = self.supabase.table("profiles").insert(payload).execute()
		return resp.data

	def get_by_id(self, user_id: str) -> Optional[Any]:
		resp = self.supabase.table("profiles").select("*").eq("id", user_id).single().execute()
		return resp.data

	def get_by_email(self, email: str) -> Optional[Any]:
		resp = self.supabase.table("profiles").select("*").eq("email", email).single().execute()
		return resp.data

	def get_by_username(self, username: str) -> Optional[Any]:
		resp = self.supabase.table("profiles").select("*").eq("username", username).single().execute()
		return resp.data

	def update_username(self, user_id: str, new_username: str) -> Any:
		resp = self.supabase.table("profiles").update({"username": new_username}).eq("id", user_id).execute()
		return resp.data

	def delete_profile(self, user_id: str) -> Any:
		resp = self.supabase.table("profiles").delete().eq("id", user_id).execute()
		return resp.data


def get_crud(supabase_client: Client) -> UserCRUD:
	"""Convenience factory to create a `UserCRUD` instance."""
	return UserCRUD(supabase_client)

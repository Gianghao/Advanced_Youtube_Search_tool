from typing import Any, Dict, List, Optional
from supabase import Client

class BaseCRUD:
    def __init__(self, supabase_client: Client, table_name: str):
        self.supabase = supabase_client
        self.table_name = table_name

    def get(self, id: Any) -> Optional[Dict[str, Any]]:
        resp = self.supabase.table(self.table_name).select("*").eq("id", id).single().execute()
        return resp.data

    def get_all(self) -> List[Dict[str, Any]]:
        resp = self.supabase.table(self.table_name).select("*").execute()
        return resp.data

    def create(self, obj_in: Dict[str, Any]) -> Dict[str, Any]:
        resp = self.supabase.table(self.table_name).insert(obj_in).execute()
        return resp.data

    def update(self, id: Any, obj_in: Dict[str, Any]) -> Dict[str, Any]:
        resp = self.supabase.table(self.table_name).update(obj_in).eq("id", id).execute()
        return resp.data

    def remove(self, id: Any) -> Dict[str, Any]:
        resp = self.supabase.table(self.table_name).delete().eq("id", id).execute()
        return resp.data

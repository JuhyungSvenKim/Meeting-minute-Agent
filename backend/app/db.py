from functools import lru_cache

from supabase import Client, create_client

from .config import get_settings


@lru_cache
def get_supabase() -> Client:
    s = get_settings()
    if not s.SUPABASE_URL or not s.SUPABASE_SERVICE_ROLE_KEY:
        raise RuntimeError(
            "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in .env"
        )
    return create_client(s.SUPABASE_URL, s.SUPABASE_SERVICE_ROLE_KEY)

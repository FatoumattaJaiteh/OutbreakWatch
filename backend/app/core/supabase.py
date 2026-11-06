import logging
from typing import Optional
from supabase import create_client, Client
from app.core.config import settings

logger = logging.getLogger("outbreakwatch.supabase")

_supabase_client: Optional[Client] = None
_supabase_admin_client: Optional[Client] = None


def get_supabase_client() -> Optional[Client]:
    """
    Returns an initialized Supabase client with standard anon key.
    Returns None if SUPABASE_URL or SUPABASE_ANON_KEY are missing.
    """
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client

    if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
        logger.warning(
            "Supabase credentials (SUPABASE_URL, SUPABASE_ANON_KEY) are not set. "
            "Database operations requiring Supabase will fail until configured."
        )
        return None

    try:
        _supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
        return _supabase_client
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {e}")
        return None


def get_supabase_admin() -> Optional[Client]:
    """
    Returns an initialized Supabase client with service-role key (bypasses RLS for backend admin tasks).
    Falls back to standard client if service role key is not provided.
    """
    global _supabase_admin_client
    if _supabase_admin_client is not None:
        return _supabase_admin_client

    key = settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_ANON_KEY
    if not settings.SUPABASE_URL or not key:
        logger.warning("Supabase credentials not configured.")
        return None

    try:
        _supabase_admin_client = create_client(settings.SUPABASE_URL, key)
        return _supabase_admin_client
    except Exception as e:
        logger.error(f"Failed to initialize Supabase admin client: {e}")
        return None


import logging
import uuid
from datetime import datetime, timezone
from typing import List, Optional
from app.core.supabase import get_supabase_client, get_supabase_admin
from app.schemas.outbreak import OutbreakCreate, OutbreakUpdate

logger = logging.getLogger("outbreakwatch.service.outbreak")

# In-memory fallback dataset for development before Supabase keys are configured
_DEMO_OUTBREAKS = [
    {
        "id": "e8a93cb0-a54b-4b21-829d-5f33a82e9b01",
        "name": "Ebola Outbreak 2026",
        "disease": "Ebola Virus Disease (Sudan / Zaire strain)",
        "description": "Active cluster of viral hemorrhagic fever identified with active contact tracing and isolation measures in effect.",
        "status": "active",
        "severity": "critical",
        "epicenter_location": "Beni & Butembo Districts",
        "country": "Democratic Republic of the Congo",
        "latitude": 0.4911,
        "longitude": 29.4731,
        "symptoms_checklist": [
            "Sudden high fever (> 38.5°C)",
            "Intense physical weakness & fatigue",
            "Severe muscle pain and headache",
            "Sore throat",
            "Vomiting and persistent diarrhea",
            "Unexplained bleeding or bruising (gums, stool, skin)"
        ],
        "guidance_notes": "Avoid direct contact with bodily fluids. Report immediately to the nearest isolation and triage center. Do not wash or prepare deceased individuals without protective public health teams.",
        "total_cases_reported": 42,
        "confirmed_cases": 18,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": "f128bcde-1290-4123-90ab-abcdef123456",
        "name": "Cholera Alert 2026",
        "disease": "Vibrio cholerae",
        "description": "Acute watery diarrheal disease spike linked to seasonal flooding and compromised water sanitation infrastructure.",
        "status": "active",
        "severity": "high",
        "epicenter_location": "Lusaka Peri-urban zones",
        "country": "Zambia",
        "latitude": -15.3875,
        "longitude": 28.3228,
        "symptoms_checklist": [
            "Profuse watery diarrhea ('rice water' stools)",
            "Rapid dehydration and excessive thirst",
            "Leg cramps",
            "Rapid heart rate and low blood pressure",
            "Dry mucous membranes"
        ],
        "guidance_notes": "Use only boiled or chlorinated water. Administer Oral Rehydration Salts (ORS) promptly upon onset.",
        "total_cases_reported": 115,
        "confirmed_cases": 64,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
]


class OutbreakService:
    @staticmethod
    def list_outbreaks(status: Optional[str] = None) -> List[dict]:
        client = get_supabase_client()
        if client:
            try:
                query = client.table("outbreaks").select("*")
                if status:
                    query = query.eq("status", status)
                res = query.order("created_at", desc=True).execute()
                return res.data or []
            except Exception as e:
                logger.error(f"Supabase query error: {e}, falling back to demo storage")

        if status:
            return [o for o in _DEMO_OUTBREAKS if o.get("status") == status]
        return _DEMO_OUTBREAKS

    @staticmethod
    def get_outbreak(outbreak_id: str) -> Optional[dict]:
        client = get_supabase_client()
        if client:
            try:
                res = client.table("outbreaks").select("*").eq("id", outbreak_id).single().execute()
                return res.data
            except Exception as e:
                logger.error(f"Supabase get error: {e}")

        for o in _DEMO_OUTBREAKS:
            if o["id"] == outbreak_id:
                return o
        return None

    @staticmethod
    def create_outbreak(data: OutbreakCreate) -> dict:
        admin_client = get_supabase_admin() or get_supabase_client()
        new_record = data.model_dump()
        new_record["id"] = str(uuid.uuid4())
        new_record["created_at"] = datetime.now(timezone.utc).isoformat()
        new_record["updated_at"] = datetime.now(timezone.utc).isoformat()
        new_record["total_cases_reported"] = 0
        new_record["confirmed_cases"] = 0

        if admin_client:
            try:
                res = admin_client.table("outbreaks").insert(new_record).execute()
                if res.data:
                    return res.data[0]
            except Exception as e:
                logger.error(f"Supabase create error: {e}, caching locally")

        _DEMO_OUTBREAKS.insert(0, new_record)
        return new_record

    @staticmethod
    def update_outbreak(outbreak_id: str, data: OutbreakUpdate) -> Optional[dict]:
        update_data = {k: v for k, v in data.model_dump().items() if v is not None}
        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()

        admin_client = get_supabase_admin() or get_supabase_client()
        if admin_client:
            try:
                res = admin_client.table("outbreaks").update(update_data).eq("id", outbreak_id).execute()
                if res.data:
                    return res.data[0]
            except Exception as e:
                logger.error(f"Supabase update error: {e}")

        for o in _DEMO_OUTBREAKS:
            if o["id"] == outbreak_id:
                o.update(update_data)
                return o
        return None


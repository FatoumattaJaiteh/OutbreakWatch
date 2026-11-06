import logging
import uuid
from datetime import datetime, timezone
from typing import List, Optional
from app.core.supabase import get_supabase_client, get_supabase_admin
from app.schemas.report import CaseReportCreate, CaseReportStatusUpdate
from app.services.outbreak_service import OutbreakService

logger = logging.getLogger("outbreakwatch.service.report")

_DEMO_REPORTS = [
    {
        "id": "c1001-2026-demo-uuid",
        "outbreak_id": "e8a93cb0-a54b-4b21-829d-5f33a82e9b01",
        "outbreak_name": "Ebola Outbreak 2026",
        "reporter_type": "healthcare_worker",
        "patient_name": "Amara Diallo",
        "patient_age": 34,
        "patient_gender": "female",
        "contact_phone": "+243 81 234 5678",
        "contact_email": "clinic.beni@healthnet.org",
        "location_address": "Zone de Sante de Butembo, Quartier Matonge",
        "region": "North Kivu",
        "country": "DR Congo",
        "symptoms_experienced": [
            "Sudden high fever (> 38.5°C)",
            "Unexplained bleeding or bruising (gums, stool, skin)",
            "Vomiting and persistent diarrhea"
        ],
        "symptom_onset_date": "2026-11-02",
        "had_contact_with_case": True,
        "recent_travel_history": "Attended funeral in neighboring village 6 days ago",
        "status": "confirmed",
        "triage_priority": "emergency",
        "additional_notes": "Admitted to rapid isolation ward. Hydration and mAb114 therapy initiated.",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
]


class ReportService:
    @staticmethod
    def calculate_triage_priority(report_data: CaseReportCreate) -> str:
        score = 0
        symptom_count = len(report_data.symptoms_experienced)
        if symptom_count >= 4:
            score += 3
        elif symptom_count >= 2:
            score += 2
        else:
            score += 1

        if report_data.had_contact_with_case:
            score += 3

        # Severe symptoms indicators
        severe_keywords = ["bleed", "hemorrhage", "vomit", "coma", "rice water", "unconscious"]
        for sym in report_data.symptoms_experienced:
            if any(k in sym.lower() for k in severe_keywords):
                score += 2
                break

        if score >= 5:
            return "emergency"
        elif score >= 3:
            return "urgent"
        return "routine"

    @staticmethod
    def create_report(data: CaseReportCreate) -> dict:
        client = get_supabase_admin() or get_supabase_client()
        outbreak = OutbreakService.get_outbreak(data.outbreak_id)
        outbreak_name = outbreak["name"] if outbreak else "Unknown Outbreak"

        priority = ReportService.calculate_triage_priority(data)
        record = data.model_dump()
        record["id"] = str(uuid.uuid4())
        record["outbreak_name"] = outbreak_name
        record["triage_priority"] = priority
        record["status"] = "suspected"
        record["created_at"] = datetime.now(timezone.utc).isoformat()
        record["updated_at"] = datetime.now(timezone.utc).isoformat()
        if record.get("symptom_onset_date"):
            record["symptom_onset_date"] = str(record["symptom_onset_date"])

        if client:
            try:
                res = client.table("case_reports").insert(record).execute()
                if res.data:
                    return res.data[0]
            except Exception as e:
                logger.error(f"Supabase report insert error: {e}, caching locally")

        _DEMO_REPORTS.insert(0, record)
        return record

    @staticmethod
    def list_reports(outbreak_id: Optional[str] = None, status: Optional[str] = None) -> List[dict]:
        client = get_supabase_client()
        if client:
            try:
                query = client.table("case_reports").select("*")
                if outbreak_id:
                    query = query.eq("outbreak_id", outbreak_id)
                if status:
                    query = query.eq("status", status)
                res = query.order("created_at", desc=True).execute()
                return res.data or []
            except Exception as e:
                logger.error(f"Supabase list reports error: {e}")

        reports = _DEMO_REPORTS
        if outbreak_id:
            reports = [r for r in reports if r.get("outbreak_id") == outbreak_id]
        if status:
            reports = [r for r in reports if r.get("status") == status]
        return reports

    @staticmethod
    def get_report(report_id: str) -> Optional[dict]:
        client = get_supabase_client()
        if client:
            try:
                res = client.table("case_reports").select("*").eq("id", report_id).single().execute()
                return res.data
            except Exception as e:
                logger.error(f"Supabase get report error: {e}")

        for r in _DEMO_REPORTS:
            if r["id"] == report_id:
                return r
        return None

    @staticmethod
    def update_report_status(report_id: str, update: CaseReportStatusUpdate) -> Optional[dict]:
        client = get_supabase_admin() or get_supabase_client()
        update_data = {k: v for k, v in update.model_dump().items() if v is not None}
        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()

        if client:
            try:
                res = client.table("case_reports").update(update_data).eq("id", report_id).execute()
                if res.data:
                    return res.data[0]
            except Exception as e:
                logger.error(f"Supabase update report error: {e}")

        for r in _DEMO_REPORTS:
            if r["id"] == report_id:
                r.update(update_data)
                return r
        return None


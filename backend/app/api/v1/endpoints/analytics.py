from fastapi import APIRouter
from app.services.outbreak_service import OutbreakService
from app.services.report_service import ReportService

router = APIRouter()


@router.get("/summary", summary="Outbreak and surveillance summary statistics")
def get_surveillance_summary():
    """Retrieve top-level operational metrics: total outbreaks, active outbreaks, total reported cases, triage counts."""
    outbreaks = OutbreakService.list_outbreaks()
    reports = ReportService.list_reports()

    active_outbreaks = [o for o in outbreaks if o.get("status") == "active"]
    emergency_reports = [r for r in reports if r.get("triage_priority") == "emergency"]
    confirmed_reports = [r for r in reports if r.get("status") == "confirmed"]
    suspected_reports = [r for r in reports if r.get("status") == "suspected"]

    return {
        "total_tracked_outbreaks": len(outbreaks),
        "active_outbreaks_count": len(active_outbreaks),
        "total_case_reports": len(reports),
        "confirmed_cases_count": len(confirmed_reports),
        "suspected_cases_count": len(suspected_reports),
        "emergency_triage_count": len(emergency_reports),
        "recent_alerts": [
            {
                "id": o.get("id"),
                "name": o.get("name"),
                "disease": o.get("disease"),
                "severity": o.get("severity"),
                "location": o.get("epicenter_location")
            }
            for o in active_outbreaks[:5]
        ]
    }


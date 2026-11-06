from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from app.schemas.report import CaseReportCreate, CaseReportResponse, CaseReportStatusUpdate
from app.services.report_service import ReportService

router = APIRouter()


@router.post("/", response_model=CaseReportResponse, status_code=status.HTTP_201_CREATED, summary="Submit public case report")
def submit_report(report_in: CaseReportCreate):
    """
    Public form submission endpoint:
    Individuals, clinicians, or family members report symptoms, location, and exposure history.
    The system automatically scores triage priority (routine, urgent, emergency).
    """
    return ReportService.create_report(report_in)


@router.get("/", response_model=List[CaseReportResponse], summary="List case reports")
def get_reports(
    outbreak_id: Optional[str] = Query(None, description="Filter by outbreak ID"),
    status: Optional[str] = Query(None, description="Filter by status (suspected, probable, confirmed, etc.)")
):
    """Retrieve submitted reports for monitoring and response teams."""
    return ReportService.list_reports(outbreak_id=outbreak_id, status=status)


@router.get("/{report_id}", response_model=CaseReportResponse, summary="Get single report details")
def get_report(report_id: str):
    """Look up a specific case submission by reference ID."""
    report = ReportService.get_report(report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report with ID '{report_id}' not found"
        )
    return report


@router.patch("/{report_id}/status", response_model=CaseReportResponse, summary="Update case verification status")
def update_report_status(report_id: str, status_in: CaseReportStatusUpdate):
    """Admin / Epidemiologist endpoint to confirm, triage or update case verification."""
    updated = ReportService.update_report_status(report_id, status_in)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report with ID '{report_id}' not found"
        )
    return updated


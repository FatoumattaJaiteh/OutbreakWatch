from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from app.schemas.screening import (
    TravellerDeclarationCreate,
    SubmissionConfirmation,
    OfficerAssessmentRequest
)
from app.services.screening_service import ScreeningService

router = APIRouter()


# ------------------------------------------------------------------------------
# PHASE 1 & 2: TRAVELLER SUBMISSION & QR GENERATION
# ------------------------------------------------------------------------------
@router.post("/submissions", response_model=SubmissionConfirmation, status_code=status.HTTP_201_CREATED, summary="Submit Traveller Declaration")
def submit_declaration(declaration: TravellerDeclarationCreate):
    """
    Public Endpoint:
    Submits the 7-section traveller health declaration.
    Validates identity, itinerary (21-day look-back), Ebola exposure, healthcare, animal, symptoms.
    Calculates timeline, evaluates rules engine, generates cryptographic opaque token and base64 QR code.
    Zero PII is stored inside the QR code.
    """
    if not declaration.truthful_declaration:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must confirm that the information provided is truthful and accurate."
        )
    return ScreeningService.process_declaration(declaration)


@router.get("/submissions/{reference}/confirmation", summary="Retrieve Submission Confirmation")
def get_submission_confirmation(reference: str):
    """Retrieves limited confirmation data for the traveller using their reference code."""
    sub = ScreeningService.get_submission_by_reference(reference)
    if not sub:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Declaration reference not found.")
    return {
        "reference_code": sub["reference_code"],
        "traveller_name": sub["traveller"]["full_name"],
        "flight_number": sub["flight_number"],
        "arrival_airport": sub["arrival_airport"],
        "arrival_date_time": sub["arrival_date_time"],
        "status": sub["status"],
        "preliminary_risk_category": sub["preliminary_risk_category"],
        "urgent_symptom_flag": sub["urgent_symptom_flag"]
    }


# ------------------------------------------------------------------------------
# PHASE 3: AIRPORT QR SCANNING & LOOKUP
# ------------------------------------------------------------------------------
@router.get("/qr/verify/{token}", summary="Airport Officer QR Code Verification")
def verify_qr_token(token: str):
    """
    Airport Staff Endpoint:
    Resolves an opaque token scanned from a traveller's QR code or manual reference code.
    Hashes the token with SHA-256 and retrieves the authorized screening record.
    """
    # Check if input is a submission reference (e.g. EB-2026-...) as manual fallback
    if token.upper().startswith("EB-"):
        record = ScreeningService.get_submission_by_reference(token)
    else:
        record = ScreeningService.resolve_qr_token(token)

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid QR token or submission reference. Record not found."
        )

    if "error" in record:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail=record["message"]
        )

    return record


# ------------------------------------------------------------------------------
# PHASE 4: AUTHORITY DASHBOARD & CASE WORKFLOW
# ------------------------------------------------------------------------------
@router.get("/staff/dashboard", summary="Authority Dashboard Metrics")
def get_dashboard_summary():
    """Returns top-level KPIs: total declarations, awaiting review, high risk, urgent symptoms, referred cases."""
    return ScreeningService.get_dashboard_summary()


@router.get("/staff/submissions", summary="List Screening Submissions Queue")
def list_submissions(
    risk_category: Optional[str] = Query(None, description="HIGH, MODERATE, LOW, NO_IDENTIFIED_EXPOSURE"),
    status: Optional[str] = Query(None, description="submitted, awaiting_review, urgent_review, officer_assessed, referred, closed"),
    flight_number: Optional[str] = Query(None, description="Filter by flight number")
):
    """Retrieves operational screening queue for airport health personnel and surveillance officers."""
    return ScreeningService.list_submissions(
        risk_category=risk_category,
        status=status,
        flight_number=flight_number
    )


@router.get("/staff/submissions/{submission_id}", summary="Get Full Traveller Record")
def get_submission_details(submission_id: str):
    """Retrieves comprehensive 7-section record, timeline, reasons, and assessment history."""
    sub = ScreeningService.get_submission_by_id(submission_id)
    if not sub:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found.")
    return sub


@router.post("/staff/submissions/{submission_id}/assessment", summary="Record Officer Assessment")
def record_assessment(submission_id: str, assessment: OfficerAssessmentRequest):
    """
    Records official human officer assessment, clinical rationale, referral destination, and disposition.
    Preserves original preliminary category and updates case status.
    """
    sub = ScreeningService.record_officer_assessment(submission_id, assessment)
    if not sub:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found.")
    return {
        "message": "Officer assessment recorded successfully.",
        "submission_id": submission_id,
        "status": sub["status"],
        "officer_category": assessment.officer_category
    }


@router.post("/staff/submissions/{submission_id}/revoke-qr", summary="Revoke QR Code")
def revoke_qr_code(submission_id: str, reason: str = "Officer administrative revocation"):
    """Revokes active QR code in case of record compromise or data correction."""
    success = ScreeningService.revoke_qr(submission_id, reason)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found.")
    return {"message": "QR token successfully revoked.", "submission_id": submission_id}


# ------------------------------------------------------------------------------
# CONFIGURATION & REFERENCE DATA
# ------------------------------------------------------------------------------
@router.get("/admin/outbreak-areas", summary="Configured Outbreak Areas")
def get_outbreak_areas():
    """Returns list of currently active outbreak areas used by the rules engine."""
    return [
        {
            "disease_name": "Ebola Virus Disease (Sudan Strain)",
            "country_code": "UGA",
            "country_name": "Uganda",
            "affected_regions": ["Mubende", "Kassanda", "Kampala", "Kagadi"],
            "status": "active",
            "valid_from": "2026-01-01",
            "guidance_notes": "Active outbreak surveillance for travellers arriving from Uganda or border transit corridors."
        },
        {
            "disease_name": "Ebola Virus Disease (Zaire Strain)",
            "country_code": "COD",
            "country_name": "Democratic Republic of the Congo",
            "affected_regions": ["North Kivu", "Ituri"],
            "status": "active",
            "valid_from": "2026-01-01",
            "guidance_notes": "Vigilance for individuals with contact or healthcare exposure in Beni/Butembo."
        }
    ]


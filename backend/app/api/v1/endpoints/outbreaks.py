from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from app.schemas.outbreak import OutbreakCreate, OutbreakResponse, OutbreakUpdate
from app.services.outbreak_service import OutbreakService

router = APIRouter()


@router.get("/", response_model=List[OutbreakResponse], summary="List all outbreaks")
def get_outbreaks(
    status: Optional[str] = Query(None, description="Filter by status ('active', 'monitoring', 'contained')")
):
    """Retrieve all tracked disease outbreaks."""
    return OutbreakService.list_outbreaks(status=status)


@router.get("/{outbreak_id}", response_model=OutbreakResponse, summary="Get outbreak details")
def get_outbreak(outbreak_id: str):
    """Retrieve details, symptoms checklist and response guidance for a specific outbreak."""
    outbreak = OutbreakService.get_outbreak(outbreak_id)
    if not outbreak:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Outbreak with ID '{outbreak_id}' not found"
        )
    return outbreak


@router.post("/", response_model=OutbreakResponse, status_code=status.HTTP_201_CREATED, summary="Create new outbreak")
def create_outbreak(outbreak_in: OutbreakCreate):
    """
    Admin endpoint to declare a new outbreak (e.g., Ebola, Cholera, Mpox).
    Configures the disease parameters and dynamic symptom checklist for public reporting.
    """
    return OutbreakService.create_outbreak(outbreak_in)


@router.patch("/{outbreak_id}", response_model=OutbreakResponse, summary="Update outbreak status")
def update_outbreak(outbreak_id: str, outbreak_in: OutbreakUpdate):
    """Update outbreak details, status or guidance notes."""
    updated = OutbreakService.update_outbreak(outbreak_id, outbreak_in)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Outbreak with ID '{outbreak_id}' not found"
        )
    return updated


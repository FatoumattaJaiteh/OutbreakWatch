from fastapi import APIRouter
from app.api.v1.endpoints import outbreaks, reports, analytics, screening, auth

api_router = APIRouter()

# Authentication & User/Role Management (Section 4 & 14)
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication & Access Control"])

# Core Ebola Screening System Endpoints (Doc Specification)
api_router.include_router(screening.router, tags=["Ebola Traveller Screening & QR Verification"])

# General Surveillance & Outbreak Tracking
api_router.include_router(outbreaks.router, prefix="/outbreaks", tags=["Outbreak Directory"])
api_router.include_router(reports.router, prefix="/reports", tags=["Public Case Reports"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Surveillance Analytics"])

from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field


class CaseReportCreate(BaseModel):
    outbreak_id: str = Field(..., description="Target outbreak UUID")
    reporter_type: str = Field("self", description="self, healthcare_worker, family, observer")
    patient_name: str = Field(..., min_length=2, description="Patient or individual full name")
    patient_age: Optional[int] = Field(None, ge=0, le=125)
    patient_gender: Optional[str] = Field("undisclosed", description="male, female, other, undisclosed")
    contact_phone: str = Field(..., description="Active phone number for rapid health response contact")
    contact_email: Optional[EmailStr] = None
    location_address: str = Field(..., description="Village, street, city or neighborhood")
    region: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    symptoms_experienced: List[str] = Field(default_factory=list, description="Array of reported symptoms")
    symptom_onset_date: Optional[date] = None
    had_contact_with_case: bool = Field(False, description="Whether subject was in proximity to known infected case")
    recent_travel_history: Optional[str] = Field(None, description="Travel details in the last 21 days")
    additional_notes: Optional[str] = None


class CaseReportStatusUpdate(BaseModel):
    status: str = Field(..., description="suspected, probable, confirmed, discarded, recovered, deceased")
    triage_priority: Optional[str] = Field(None, description="routine, urgent, emergency")
    admin_notes: Optional[str] = None


class CaseReportResponse(BaseModel):
    id: str
    outbreak_id: str
    outbreak_name: Optional[str] = None
    reporter_type: str
    patient_name: str
    patient_age: Optional[int] = None
    patient_gender: Optional[str] = None
    contact_phone: str
    contact_email: Optional[str] = None
    location_address: str
    region: Optional[str] = None
    country: Optional[str] = None
    symptoms_experienced: List[str] = []
    symptom_onset_date: Optional[date] = None
    had_contact_with_case: bool = False
    recent_travel_history: Optional[str] = None
    status: str = "suspected"
    triage_priority: str = "routine"
    additional_notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


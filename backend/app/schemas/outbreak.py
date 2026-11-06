from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class OutbreakBase(BaseModel):
    name: str = Field(..., description="Outbreak display name, e.g. 'Ebola Outbreak 2026'")
    disease: str = Field(..., description="Disease type, e.g. 'Ebola Virus Disease'")
    description: Optional[str] = Field(None, description="Overview and current situation report")
    status: str = Field("active", description="Status: 'active', 'monitoring', 'contained', 'archived'")
    severity: str = Field("high", description="Severity level: 'low', 'medium', 'high', 'critical'")
    epicenter_location: str = Field(..., description="Primary geographic location / city / region")
    country: Optional[str] = Field(None, description="Country name")
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    symptoms_checklist: List[str] = Field(
        default_factory=list,
        description="List of symptoms dynamically prompted on the public submission form"
    )
    guidance_notes: Optional[str] = Field(
        None,
        description="Public health safety instructions displayed to individuals reporting"
    )


class OutbreakCreate(OutbreakBase):
    pass


class OutbreakUpdate(BaseModel):
    name: Optional[str] = None
    disease: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    severity: Optional[str] = None
    epicenter_location: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    symptoms_checklist: Optional[List[str]] = None
    guidance_notes: Optional[str] = None


class OutbreakResponse(OutbreakBase):
    id: str
    total_cases_reported: Optional[int] = 0
    confirmed_cases: Optional[int] = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


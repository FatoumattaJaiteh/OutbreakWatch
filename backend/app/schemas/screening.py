from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field


# ------------------------------------------------------------------------------
# SECTION 1: Personal & Flight Information
# ------------------------------------------------------------------------------
class PersonalInformation(BaseModel):
    full_name: str = Field(..., min_length=2, description="Full name as shown on travel passport")
    date_of_birth: date = Field(..., description="Date of birth")
    sex: str = Field(..., description="male, female, other, undisclosed")
    nationality: str = Field(..., description="Nationality country name or code")
    residence_country: str = Field(..., description="Country of permanent residence")
    passport_number: Optional[str] = Field(None, description="Passport or travel document number")
    issuing_country: Optional[str] = None
    phone_number: str = Field(..., description="Active international phone number with country code")
    email: Optional[EmailStr] = None
    address_in_gambia: str = Field(..., description="Intended stay address, hotel, or residence in The Gambia")
    flight_number: str = Field(..., description="Flight number, e.g., SN241, W3302")
    airline: Optional[str] = None
    arrival_airport: str = Field("Banjul International Airport (BJL)", description="Designated port of entry")
    arrival_date_time: datetime = Field(..., description="Scheduled arrival date and time")


# ------------------------------------------------------------------------------
# SECTION 2: Itinerary & Country History (21-Day Look-Back)
# ------------------------------------------------------------------------------
class ItineraryEntry(BaseModel):
    country_name: str
    city_or_district: Optional[str] = None
    entry_date: date
    departure_date: date
    purpose_of_visit: Optional[str] = "Tourism"  # Tourism, Business, Employment, Medical, Family, Humanitarian, Other
    accommodation_type: Optional[str] = "Hotel"
    is_transit: bool = False
    transit_airport: Optional[str] = None
    left_transit_airport: bool = False


# ------------------------------------------------------------------------------
# SECTION 3: Exposure to Ebola Cases
# ------------------------------------------------------------------------------
class ExposureEvent(BaseModel):
    question_key: str
    question_label: str
    answer: str = Field(..., description="Yes, No, or Unsure")
    exposure_date: Optional[date] = None
    location_details: Optional[str] = None
    contact_type: Optional[str] = None
    ppe_used: Optional[str] = None
    ppe_failure_or_breach: bool = False
    notes: Optional[str] = None


# ------------------------------------------------------------------------------
# SECTION 4: Healthcare & Occupational Exposure
# ------------------------------------------------------------------------------
class HealthcareEvent(BaseModel):
    event_type: str
    answer: str = Field(..., description="Yes, No, or Unsure")
    facility_name: Optional[str] = None
    facility_location: Optional[str] = None
    activity_dates: Optional[str] = None
    role_or_occupation: Optional[str] = None
    ppe_details: Optional[str] = None
    incident_details: Optional[str] = None


# ------------------------------------------------------------------------------
# SECTION 5: Animal & Environmental Exposure
# ------------------------------------------------------------------------------
class EnvironmentalEvent(BaseModel):
    event_type: str
    answer: str = Field(..., description="Yes, No, or Unsure")
    species_or_animal: Optional[str] = None
    location_details: Optional[str] = None
    event_date: Optional[date] = None
    contact_details: Optional[str] = None


# ------------------------------------------------------------------------------
# SECTION 6: Current Health Condition & Symptoms
# ------------------------------------------------------------------------------
class SymptomReport(BaseModel):
    symptoms_list: List[str] = Field(default_factory=list)
    has_fever: bool = False
    body_temperature: Optional[float] = None
    unexplained_bleeding: bool = False
    symptom_onset_date: Optional[date] = None
    symptoms_still_present: bool = True
    symptoms_worsened: bool = False
    received_medical_care: bool = False
    ebola_tested: str = Field("No", description="Yes, No, or Pending")
    test_result: Optional[str] = None


# ------------------------------------------------------------------------------
# SECTION 7: Complete Declaration Submission
# ------------------------------------------------------------------------------
class TravellerDeclarationCreate(BaseModel):
    personal: PersonalInformation
    itinerary: List[ItineraryEntry] = Field(default_factory=list)
    exposures: List[ExposureEvent] = Field(default_factory=list)
    healthcare: List[HealthcareEvent] = Field(default_factory=list)
    environmental: List[EnvironmentalEvent] = Field(default_factory=list)
    symptoms: SymptomReport
    truthful_declaration: bool = Field(..., description="Traveller confirms information is accurate")


# ------------------------------------------------------------------------------
# CONFIRMATION & QR RESPONSES
# ------------------------------------------------------------------------------
class SubmissionConfirmation(BaseModel):
    submission_id: str
    reference_code: str
    traveller_name: str
    flight_number: str
    arrival_airport: str
    arrival_date_time: datetime
    submitted_at: datetime
    preliminary_risk_category: str
    urgent_symptom_flag: bool
    qr_token: str
    qr_code_base64: str
    instructions: str


# ------------------------------------------------------------------------------
# OFFICER ASSESSMENT & REVIEW
# ------------------------------------------------------------------------------
class OfficerAssessmentRequest(BaseModel):
    officer_name: str
    officer_role: str
    officer_category: str = Field(..., description="HIGH, MODERATE, LOW, NO_IDENTIFIED_EXPOSURE, CLEARED")
    officer_rationale: str
    referral_destination: Optional[str] = None
    referral_notes: Optional[str] = None
    disposition: Optional[str] = "Cleared for entry"  # Cleared for entry, Secondary screening, Isolation referral, 21-day monitoring


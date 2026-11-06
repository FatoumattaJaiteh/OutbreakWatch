import logging
import uuid
from datetime import date, datetime, timedelta, timezone
from typing import Dict, List, Optional
from app.core.config import settings
from app.core.supabase import get_supabase_client, get_supabase_admin
from app.schemas.screening import (
    TravellerDeclarationCreate,
    SubmissionConfirmation,
    OfficerAssessmentRequest
)
from app.services.triage_engine import TriageEngine, RULE_SET_VERSION
from app.services.qr_service import QRService

logger = logging.getLogger("outbreakwatch.service.screening")

# In-memory storage cache for local speed and seamless operation
_STORE_TRAVELLERS: Dict[str, dict] = {}
_STORE_SUBMISSIONS: Dict[str, dict] = {}
_STORE_TOKENS: Dict[str, dict] = {}  # token_hash -> token_record
_TOKEN_TO_SUBMISSION: Dict[str, str] = {}  # token_hash -> submission_id
_STORE_ASSESSMENTS: Dict[str, list] = {}  # submission_id -> list of assessments


class ScreeningService:
    @staticmethod
    def _generate_reference_code() -> str:
        num = uuid.uuid4().hex[:6].upper()
        year = datetime.now(timezone.utc).year
        return f"EB-{year}-{num}"

    @staticmethod
    def process_declaration(declaration: TravellerDeclarationCreate) -> SubmissionConfirmation:
        """
        Processes 7-section traveller declaration:
        1. Calculates age and timeline
        2. Applies TriageEngine
        3. Creates QR token with SHA-256 hash
        4. Saves record
        5. Returns confirmation with QR image
        """
        now_utc = datetime.now(timezone.utc)
        traveller_id = str(uuid.uuid4())
        submission_id = str(uuid.uuid4())
        ref_code = ScreeningService._generate_reference_code()

        # 1. Age calculation
        calc_age = TriageEngine.calculate_age(
            declaration.personal.date_of_birth,
            declaration.personal.arrival_date_time.date()
        )

        # 2. Timeline calculation (Section 7)
        exposure_dates = [
            exp.exposure_date for exp in declaration.exposures if exp.exposure_date
        ]
        first_exposure = min(exposure_dates) if exposure_dates else None
        last_exposure = max(exposure_dates) if exposure_dates else None
        arrival_d = declaration.personal.arrival_date_time.date()

        days_since_exposure = (arrival_d - last_exposure).days if last_exposure else None
        within_21_days = (days_since_exposure is not None and 0 <= days_since_exposure <= 21)
        monitoring_end_date = (last_exposure + timedelta(days=21)) if last_exposure else None

        # 3. Triage Risk Evaluation
        category, reasons, urgent_flag = TriageEngine.evaluate(
            itinerary=declaration.itinerary,
            exposures=declaration.exposures,
            healthcare=declaration.healthcare,
            environmental=declaration.environmental,
            symptoms=declaration.symptoms
        )

        # Determine initial case status
        initial_status = "submitted"
        if urgent_flag:
            initial_status = "urgent_review"
        elif category in ("HIGH", "MODERATE", "MANUAL_REVIEW"):
            initial_status = "awaiting_review"

        # 4. Cryptographic QR Token Generation (Section 9)
        raw_token = QRService.generate_token()
        token_hash = QRService.hash_token(raw_token)
        expires_at = now_utc + timedelta(days=7)

        # QR payload: pure URL with opaque token only, NO PII
        verification_payload = QRService.build_verification_payload(raw_token)
        qr_image_base64 = QRService.generate_qr_image_base64(verification_payload)

        # 5. Assemble Records
        traveller_record = {
            "id": traveller_id,
            "full_name": declaration.personal.full_name,
            "date_of_birth": str(declaration.personal.date_of_birth),
            "calculated_age": calc_age,
            "sex": declaration.personal.sex,
            "nationality": declaration.personal.nationality,
            "residence_country": declaration.personal.residence_country,
            "passport_number": declaration.personal.passport_number,
            "issuing_country": declaration.personal.issuing_country,
            "phone_number": declaration.personal.phone_number,
            "email": declaration.personal.email,
            "address_in_gambia": declaration.personal.address_in_gambia,
            "created_at": now_utc.isoformat()
        }

        submission_record = {
            "id": submission_id,
            "traveller_id": traveller_id,
            "reference_code": ref_code,
            "flight_number": declaration.personal.flight_number,
            "airline": declaration.personal.airline,
            "arrival_airport": declaration.personal.arrival_airport,
            "arrival_date_time": declaration.personal.arrival_date_time.isoformat(),
            "submitted_at": now_utc.isoformat(),
            "status": initial_status,
            "preliminary_risk_category": category,
            "urgent_symptom_flag": urgent_flag,
            "manual_review_reasons": reasons,
            "rule_set_version": RULE_SET_VERSION,
            # Embedded full details for rapid officer review
            "traveller": traveller_record,
            "itinerary": [it.model_dump(mode="json") for it in declaration.itinerary],
            "exposures": [exp.model_dump(mode="json") for exp in declaration.exposures],
            "healthcare": [hc.model_dump(mode="json") for hc in declaration.healthcare],
            "environmental": [env.model_dump(mode="json") for env in declaration.environmental],
            "symptoms": declaration.symptoms.model_dump(mode="json"),
            "timeline": {
                "first_possible_exposure": str(first_exposure) if first_exposure else None,
                "last_possible_exposure": str(last_exposure) if last_exposure else None,
                "arrival_date": str(arrival_d),
                "days_since_last_exposure": days_since_exposure,
                "within_21_days": within_21_days,
                "monitoring_end_date": str(monitoring_end_date) if monitoring_end_date else None,
            },
            "created_at": now_utc.isoformat(),
            "updated_at": now_utc.isoformat()
        }

        token_record = {
            "id": str(uuid.uuid4()),
            "submission_id": submission_id,
            "token_hash": token_hash,
            "status": "active",
            "issued_at": now_utc.isoformat(),
            "expires_at": expires_at.isoformat(),
            "scan_count": 0
        }

        # Save to memory store
        _STORE_TRAVELLERS[traveller_id] = traveller_record
        _STORE_SUBMISSIONS[submission_id] = submission_record
        _STORE_TOKENS[token_hash] = token_record
        _TOKEN_TO_SUBMISSION[token_hash] = submission_id

        # Also attempt Supabase insert if available
        client = get_supabase_admin() or get_supabase_client()
        if client:
            try:
                client.table("travellers").insert(traveller_record).execute()
                client.table("submissions").insert({
                    "id": submission_id,
                    "traveller_id": traveller_id,
                    "reference_code": ref_code,
                    "flight_number": declaration.personal.flight_number,
                    "airline": declaration.personal.airline,
                    "arrival_airport": declaration.personal.arrival_airport,
                    "arrival_date_time": declaration.personal.arrival_date_time.isoformat(),
                    "submitted_at": now_utc.isoformat(),
                    "status": initial_status,
                    "preliminary_risk_category": category,
                    "urgent_symptom_flag": urgent_flag,
                    "manual_review_reasons": reasons,
                    "rule_set_version": RULE_SET_VERSION
                }).execute()
                client.table("qr_tokens").insert(token_record).execute()
            except Exception as e:
                logger.warning(f"Supabase async save skipped/failed: {e}")

        instructions = (
            "Present this QR code to the Ministry of Health airport screening officer upon disembarkation at "
            f"{declaration.personal.arrival_airport}. You may download the QR code image or save a screenshot as backup."
        )

        return SubmissionConfirmation(
            submission_id=submission_id,
            reference_code=ref_code,
            traveller_name=declaration.personal.full_name,
            flight_number=declaration.personal.flight_number,
            arrival_airport=declaration.personal.arrival_airport,
            arrival_date_time=declaration.personal.arrival_date_time,
            submitted_at=now_utc,
            preliminary_risk_category=category,
            urgent_symptom_flag=urgent_flag,
            qr_token=raw_token,
            qr_code_base64=qr_image_base64,
            instructions=instructions
        )

    @staticmethod
    def resolve_qr_token(token: str) -> Optional[dict]:
        """
        Resolves opaque verification token (Phase 3 Airport Screening).
        Hashes token with SHA-256, validates status, logs scan count.
        """
        token_hash = QRService.hash_token(token)
        token_rec = _STORE_TOKENS.get(token_hash)
        if not token_rec:
            return None

        if token_rec.get("status") != "active":
            return {
                "error": "TOKEN_INACTIVE",
                "status": token_rec.get("status"),
                "message": f"This QR code is currently {token_rec.get('status')}."
            }

        token_rec["scan_count"] = token_rec.get("scan_count", 0) + 1
        token_rec["last_scanned_at"] = datetime.now(timezone.utc).isoformat()

        sub_id = _TOKEN_TO_SUBMISSION.get(token_hash)
        sub = _STORE_SUBMISSIONS.get(sub_id)
        return sub

    @staticmethod
    def get_submission_by_reference(reference_code: str) -> Optional[dict]:
        code = reference_code.strip().upper()
        for sub in _STORE_SUBMISSIONS.values():
            if sub.get("reference_code", "").upper() == code:
                return sub
        return None

    @staticmethod
    def get_submission_by_id(submission_id: str) -> Optional[dict]:
        return _STORE_SUBMISSIONS.get(submission_id)

    @staticmethod
    def list_submissions(
        risk_category: Optional[str] = None,
        status: Optional[str] = None,
        flight_number: Optional[str] = None
    ) -> List[dict]:
        subs = list(_STORE_SUBMISSIONS.values())
        if risk_category:
            subs = [s for s in subs if s.get("preliminary_risk_category") == risk_category]
        if status:
            subs = [s for s in subs if s.get("status") == status]
        if flight_number:
            subs = [s for s in subs if flight_number.lower() in s.get("flight_number", "").lower()]
        return sorted(subs, key=lambda s: s.get("submitted_at", ""), reverse=True)

    @staticmethod
    def record_officer_assessment(submission_id: str, assessment: OfficerAssessmentRequest) -> Optional[dict]:
        sub = _STORE_SUBMISSIONS.get(submission_id)
        if not sub:
            return None

        now_utc = datetime.now(timezone.utc).isoformat()
        assessment_record = {
            "id": str(uuid.uuid4()),
            "submission_id": submission_id,
            "officer_name": assessment.officer_name,
            "officer_role": assessment.officer_role,
            "officer_category": assessment.officer_category,
            "officer_rationale": assessment.officer_rationale,
            "referral_destination": assessment.referral_destination,
            "referral_notes": assessment.referral_notes,
            "disposition": assessment.disposition,
            "assessed_at": now_utc
        }

        # Update submission status
        if assessment.referral_destination:
            sub["status"] = "referred"
        elif assessment.officer_category == "CLEARED" or assessment.disposition == "Cleared for entry":
            sub["status"] = "closed"
        else:
            sub["status"] = "officer_assessed"

        sub["officer_assessment"] = assessment_record
        sub["updated_at"] = now_utc

        if submission_id not in _STORE_ASSESSMENTS:
            _STORE_ASSESSMENTS[submission_id] = []
        _STORE_ASSESSMENTS[submission_id].append(assessment_record)

        return sub

    @staticmethod
    def revoke_qr(submission_id: str, reason: str = "Administrative review") -> bool:
        sub = _STORE_SUBMISSIONS.get(submission_id)
        if not sub:
            return False

        for token_hash, sid in _TOKEN_TO_SUBMISSION.items():
            if sid == submission_id:
                rec = _STORE_TOKENS.get(token_hash)
                if rec:
                    rec["status"] = "revoked"
                    rec["revoked_at"] = datetime.now(timezone.utc).isoformat()
                    rec["revoked_reason"] = reason
        sub["status"] = "awaiting_review"
        return True

    @staticmethod
    def get_dashboard_summary() -> dict:
        subs = list(_STORE_SUBMISSIONS.values())
        total = len(subs)
        urgent = len([s for s in subs if s.get("urgent_symptom_flag")])
        awaiting = len([s for s in subs if s.get("status") in ("awaiting_review", "urgent_review")])
        high_risk = len([s for s in subs if s.get("preliminary_risk_category") == "HIGH"])
        moderate = len([s for s in subs if s.get("preliminary_risk_category") == "MODERATE"])
        low_risk = len([s for s in subs if s.get("preliminary_risk_category") == "LOW"])
        no_exposure = len([s for s in subs if s.get("preliminary_risk_category") == "NO_IDENTIFIED_EXPOSURE"])
        referred = len([s for s in subs if s.get("status") == "referred"])

        return {
            "total_declarations": total,
            "awaiting_review": awaiting,
            "urgent_symptom_flags": urgent,
            "high_risk_count": high_risk,
            "moderate_risk_count": moderate,
            "low_risk_count": low_risk,
            "no_identified_exposure_count": no_exposure,
            "referred_cases": referred,
            "recent_urgent": [
                {
                    "id": s["id"],
                    "reference_code": s["reference_code"],
                    "traveller_name": s["traveller"]["full_name"],
                    "flight_number": s["flight_number"],
                    "category": s["preliminary_risk_category"],
                    "status": s["status"],
                    "submitted_at": s["submitted_at"]
                }
                for s in subs if s.get("urgent_symptom_flag") or s.get("preliminary_risk_category") == "HIGH"
            ][:5]
        }

    @classmethod
    def seed_demo_data(cls):
        """Pre-populates demonstration cases for rapid verification and training."""
        if _STORE_SUBMISSIONS:
            return

        from app.schemas.screening import (
            PersonalInformation,
            ItineraryEntry,
            ExposureEvent,
            HealthcareEvent,
            EnvironmentalEvent,
            SymptomReport,
            TravellerDeclarationCreate
        )

        demo1 = TravellerDeclarationCreate(
            personal=PersonalInformation(
                full_name="Khadija S. Camara",
                date_of_birth=date(1992, 5, 14),
                sex="female",
                nationality="The Gambia",
                residence_country="The Gambia",
                passport_number="GAM8829104",
                phone_number="+220 732 9911",
                email="khadija.camara@gambiahealth.gm",
                address_in_gambia="Fajara M Section, Bakau, Kanifing Municipality",
                flight_number="SN241",
                airline="Brussels Airlines",
                arrival_airport="Banjul International Airport (BJL)",
                arrival_date_time=datetime.now(timezone.utc) + timedelta(hours=3)
            ),
            itinerary=[
                ItineraryEntry(
                    country_name="Uganda",
                    city_or_district="Mubende District",
                    entry_date=date(2026, 10, 15),
                    departure_date=date(2026, 11, 2),
                    purpose_of_visit="Humanitarian work",
                    accommodation_type="Healthcare facility"
                )
            ],
            exposures=[
                ExposureEvent(
                    question_key="direct_contact",
                    question_label="Direct contact with anyone diagnosed with Ebola",
                    answer="Yes",
                    exposure_date=date(2026, 10, 28),
                    location_details="Mubende Referral Clinic",
                    contact_type="Patient care / assisting triage",
                    ppe_used="Yes - Full protective gear",
                    ppe_failure_or_breach=False
                )
            ],
            healthcare=[
                HealthcareEvent(
                    event_type="Worked in an Ebola treatment facility",
                    answer="Yes",
                    facility_name="Mubende Isolation Center",
                    role_or_occupation="Infection Control Nurse"
                )
            ],
            environmental=[],
            symptoms=SymptomReport(
                symptoms_list=["Severe headache", "Extreme tiredness"],
                has_fever=False,
                body_temperature=37.2
            ),
            truthful_declaration=True
        )

        demo2 = TravellerDeclarationCreate(
            personal=PersonalInformation(
                full_name="Ebrima Barrow",
                date_of_birth=date(1985, 9, 21),
                sex="male",
                nationality="Senegal",
                residence_country="Senegal",
                passport_number="SN0091244",
                phone_number="+221 77 123 4567",
                email="ebrima.barrow@trade.sn",
                address_in_gambia="Senegambia Beach Hotel, Kololi",
                flight_number="W3302",
                airline="Arik Air",
                arrival_airport="Banjul International Airport (BJL)",
                arrival_date_time=datetime.now(timezone.utc) + timedelta(hours=1)
            ),
            itinerary=[
                ItineraryEntry(
                    country_name="Senegal",
                    city_or_district="Dakar",
                    entry_date=date(2026, 10, 20),
                    departure_date=date(2026, 11, 5),
                    purpose_of_visit="Business",
                    accommodation_type="Hotel"
                )
            ],
            exposures=[],
            healthcare=[],
            environmental=[],
            symptoms=SymptomReport(symptoms_list=[]),
            truthful_declaration=True
        )

        cls.process_declaration(demo1)
        cls.process_declaration(demo2)

ScreeningService.seed_demo_data()


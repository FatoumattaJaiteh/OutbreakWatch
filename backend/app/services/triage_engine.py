"""
Ebola Triage & Decision Support Rules Engine
Implements Section 8 of the Ministry of Health, The Gambia specification.
Version-controlled rule set: v1.0-gambia-baseline
"""

from datetime import date
from typing import List, Tuple
from app.schemas.screening import (
    ExposureEvent,
    HealthcareEvent,
    EnvironmentalEvent,
    SymptomReport,
    ItineraryEntry
)

RULE_SET_VERSION = "v1.0-gambia-baseline"

KNOWN_AFFECTED_AREAS = [
    "uganda", "democratic republic of the congo", "congo", "guinea",
    "sierra leone", "liberia", "mubende", "kassanda", "beni", "butembo"
]


class TriageEngine:
    @staticmethod
    def calculate_age(dob: date, on_date: date = None) -> int:
        if not on_date:
            on_date = date.today()
        return on_date.year - dob.year - ((on_date.month, on_date.day) < (dob.month, dob.day))

    @staticmethod
    def evaluate(
        itinerary: List[ItineraryEntry],
        exposures: List[ExposureEvent],
        healthcare: List[HealthcareEvent],
        environmental: List[EnvironmentalEvent],
        symptoms: SymptomReport
    ) -> Tuple[str, List[str], bool]:
        """
        Evaluates submitted declaration and returns:
        (preliminary_category, reasons_list, urgent_symptom_flag)
        Categories: HIGH, MODERATE, LOW, NO_IDENTIFIED_EXPOSURE, MANUAL_REVIEW
        """
        reasons: List[str] = []
        urgent_symptom_flag = False

        # ----------------------------------------------------------------------
        # 1. Clinical Symptom Trigger Check (Section 8.5)
        # ----------------------------------------------------------------------
        has_fever = symptoms.has_fever or (symptoms.body_temperature and symptoms.body_temperature >= 38.0)
        has_hemorrhage = symptoms.unexplained_bleeding or any(
            "bleed" in s.lower() or "bruis" in s.lower() for s in symptoms.symptoms_list
        )
        has_severe_gi = any(
            "vomit" in s.lower() or "diarrh" in s.lower() for s in symptoms.symptoms_list
        )

        if has_fever and has_hemorrhage:
            urgent_symptom_flag = True
            reasons.append("URGENT: Acute febrile illness with unexplained bleeding/hemorrhage reported.")
        elif has_fever and has_severe_gi:
            urgent_symptom_flag = True
            reasons.append("URGENT: Acute febrile illness with persistent vomiting and/or diarrhea reported.")
        elif has_fever or len(symptoms.symptoms_list) >= 3:
            reasons.append(f"Clinical signs reported: Fever ({symptoms.body_temperature or 'Present'}°C) and {len(symptoms.symptoms_list)} systemic symptoms.")

        # ----------------------------------------------------------------------
        # 2. High-Risk Exposure Rules Check (Section 8.2)
        # ----------------------------------------------------------------------
        high_risk_hits = []

        for exp in exposures:
            ans = exp.answer.strip().lower()
            key = exp.question_key.lower()

            if ans == "yes":
                if "direct" in key or "fluid" in key or "touch" in key or "dead" in key or "funeral" in key or "survivor" in key:
                    high_risk_hits.append(f"Reported direct exposure: {exp.question_label}")
                elif exp.ppe_failure_or_breach:
                    high_risk_hits.append(f"Reported PPE breach during exposure: {exp.question_label}")

        for hc in healthcare:
            if hc.answer.strip().lower() == "yes":
                if "needle" in hc.event_type.lower():
                    high_risk_hits.append("Reported needle-stick or sharp injury involving potentially contaminated material")
                elif "treatment" in hc.event_type.lower() or "mortuary" in hc.event_type.lower():
                    if "breach" in (hc.incident_details or "").lower() or not hc.ppe_details:
                        high_risk_hits.append(f"High-risk clinical/mortuary activity: {hc.event_type}")

        if high_risk_hits:
            reasons.extend(high_risk_hits)
            return ("HIGH", reasons, urgent_symptom_flag)

        # ----------------------------------------------------------------------
        # 3. Moderate-Risk Criteria Check (Section 8.3)
        # ----------------------------------------------------------------------
        moderate_risk_hits = []

        # Check for Unsure answers (Section 8.5: do not silently treat Unsure as No)
        unsure_exposures = [exp.question_label for exp in exposures if exp.answer.strip().lower() == "unsure"]
        if unsure_exposures:
            moderate_risk_hits.append(f"Uncertain/unconfirmed exposure history: {', '.join(unsure_exposures[:2])}")

        for hc in healthcare:
            if hc.answer.strip().lower() in ("yes", "unsure"):
                moderate_risk_hits.append(f"Healthcare or medical facility contact in affected area: {hc.event_type}")

        for env in environmental:
            if env.answer.strip().lower() == "yes":
                moderate_risk_hits.append(f"Animal or environmental exposure: {env.event_type} ({env.species_or_animal or 'wildlife'})")

        # Check travel to configured affected countries
        visited_affected_area = False
        for it in itinerary:
            country_clean = it.country_name.strip().lower()
            city_clean = (it.city_or_district or "").strip().lower()
            if any(area in country_clean or area in city_clean for area in KNOWN_AFFECTED_AREAS):
                visited_affected_area = True
                moderate_risk_hits.append(f"Travel history to configured outbreak area: {it.country_name} ({it.city_or_district or 'General'})")

        if moderate_risk_hits:
            reasons.extend(moderate_risk_hits)
            return ("MODERATE", reasons, urgent_symptom_flag)

        # ----------------------------------------------------------------------
        # 4. Low-Risk Criteria Check (Section 8.4)
        # ----------------------------------------------------------------------
        if len(symptoms.symptoms_list) > 0:
            reasons.append("Mild symptoms declared with no identified epidemiological exposure link.")
            return ("LOW", reasons, urgent_symptom_flag)

        # ----------------------------------------------------------------------
        # 5. No Identified Exposure (Section 8.4)
        # ----------------------------------------------------------------------
        reasons.append("No relevant Ebola case contact, healthcare facility exposure, or clinical symptoms declared.")
        return ("NO_IDENTIFIED_EXPOSURE", reasons, urgent_symptom_flag)


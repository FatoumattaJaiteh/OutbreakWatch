# OutbreakWatch REST API Documentation

Base URL: `http://localhost:8000/api/v1`  
Interactive Swagger UI: `http://localhost:8000/api/v1/docs`  
ReDoc: `http://localhost:8000/api/v1/redoc`

---

## 1. Outbreaks Endpoints

### List Outbreaks
- **Endpoint**: `GET /outbreaks/`
- **Query Parameters**:
  - `status` *(optional)*: `active`, `monitoring`, `contained`, `archived`
- **Response**: Array of Outbreak objects.

### Get Outbreak Details
- **Endpoint**: `GET /outbreaks/{outbreak_id}`
- **Response**: Outbreak object with symptoms checklist and guidance notes.

### Declare New Outbreak (Admin)
- **Endpoint**: `POST /outbreaks/`
- **Request Body**:
  ```json
  {
    "name": "Ebola Outbreak 2026",
    "disease": "Ebola Virus Disease",
    "description": "Active cluster of viral hemorrhagic fever in North Kivu.",
    "status": "active",
    "severity": "critical",
    "epicenter_location": "Beni District",
    "country": "DR Congo",
    "symptoms_checklist": [
      "Sudden high fever (> 38.5°C)",
      "Unexplained bleeding or bruising",
      "Persistent vomiting & diarrhea"
    ],
    "guidance_notes": "Avoid contact with bodily fluids. Call emergency hotline immediately."
  }
  ```

### Update Outbreak
- **Endpoint**: `PATCH /outbreaks/{outbreak_id}`
- **Request Body**: Partial outbreak fields (e.g. `{"status": "contained"}`).

---

## 2. Case Reports Endpoints

### Submit Case Report (Public)
- **Endpoint**: `POST /reports/`
- **Request Body**:
  ```json
  {
    "outbreak_id": "e8a93cb0-a54b-4b21-829d-5f33a82e9b01",
    "reporter_type": "self",
    "patient_name": "John Doe",
    "patient_age": 32,
    "patient_gender": "male",
    "contact_phone": "+243 81 000 0000",
    "contact_email": "john@example.com",
    "location_address": "Quartier Matonge, Beni",
    "symptoms_experienced": [
      "Sudden high fever (> 38.5°C)",
      "Unexplained bleeding or bruising"
    ],
    "symptom_onset_date": "2026-11-04",
    "had_contact_with_case": true,
    "recent_travel_history": "Attended community gathering",
    "additional_notes": "Subject has extreme fatigue"
  }
  ```
- **Response**: Created report with generated UUID, status (`suspected`), and triage priority (`emergency`).

### List Case Reports (Admin / Surveillance)
- **Endpoint**: `GET /reports/`
- **Query Parameters**:
  - `outbreak_id` *(optional)*
  - `status` *(optional)*: `suspected`, `probable`, `confirmed`, `discarded`

### Update Case Status
- **Endpoint**: `PATCH /reports/{report_id}/status`
- **Request Body**:
  ```json
  {
    "status": "confirmed",
    "admin_notes": "Lab PCR returned positive"
  }
  ```

---

## 3. Analytics Endpoints

### Surveillance Summary
- **Endpoint**: `GET /analytics/summary`
- **Response**: Aggregated counts of outbreaks, total reports, emergency triage alerts, and confirmed cases.


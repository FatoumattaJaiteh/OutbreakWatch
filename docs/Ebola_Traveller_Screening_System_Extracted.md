EBOLA TRAVELLERSCREENING & QR CODEVERIFICATION SYSTEM
System Analysis, Requirements and Technical Design Documentation
Proposed for: Ministry of Health, The Gambia
Prepared as a software development project document
TECHNOLOGY STACKPython • JavaScript • HTML5 • CSS3 • Supaase
Document Control
Item
Description
Document title
Ebola Traveller Screening & QR Code Verification System
Version
1.0 – Proposed design
Status
Requirements and technical design baseline; requires Ministry review
Intended audience
Ministry of Health leadership, public-health officers, airport health staff, developers, system administrators
Primary users
Travellers, airport screening personnel, surveillance officers, administrators
Technology
Python backend, JavaScript frontend, HTML/CSS, SUPAASE database
Important Public-Health and Governance Notice
This document describes a proposed screening, information-management and referral-support system. It is not a clinical protocol, diagnostic tool or substitute for national case definitions, WHO guidance, laboratory testing or decisions made by qualified public-health personnel.
Before operational use, the Ministry of Health must approve the screening questionnaire, outbreak-area configuration, risk rules, referral pathways, data-retention schedule, privacy notice and operating procedures. The system must not automatically diagnose Ebola, deny travel, or make coercive decisions solely from an algorithmic category.
Outbreak locations, affected districts, relevant exposure definitions and guidance can change. These must be managed through a controlled administrator configuration process with effective dates, version history and approval records—not hardcoded into application logic.
Table of Contents
1. Executive Summary
2. Background and Problem Statement
3. Aim, Objectives and Scope
4. Stakeholders and User Roles
5. System Overview and Four Operational Phases
6. Functional Requirements
7. Traveller Screening Form Specification
8. Risk Classification and Decision Support
9. QR Code Design and Verification
10. Authority Dashboard and Case Workflow
11. System Architecture and Technology Stack
12. Database Design
13. Data Validation and Business Rules
14. Security, Privacy and Audit
15. Non-Functional Requirements
16. User Interface and Accessibility
17. Reports and Monitoring
18. Testing and Quality Assurance
19. Deployment and Operations
20. Development Plan and Deliverables
21. Risks, Assumptions and Dependencies
22. Acceptance Criteria
Appendices
In Microsoft Word, an automatic table of contents can be inserted from References → Table of Contents after applying heading styles. The section list above is a navigation guide.
1. Executive Summary
The proposed Ebola Traveller Screening & QR Code Verification System is a secure web application intended to collect traveller declarations before or during arrival processing, assess reported epidemiological exposure using Ministry-approved rules, generate a unique QR code, and allow authorised airport and public-health personnel to retrieve and review the traveller’s record.
Travellers complete a guided, multi-section declaration. On successful submission, the backend validates the information, stores it in MySQL, records the rule-set version used, and issues a QR code containing only a random, non-meaningful verification token. The traveller sees a confirmation page with their name and QR code and can save the image or use the device’s normal screenshot function.
At the airport, an authorised officer signs in and scans the QR code. The system resolves the token and displays the traveller’s record according to the officer’s permissions. The dashboard highlights the preliminary category, relevant exposure answers, symptom declarations, last possible exposure date, and recommended workflow actions. A qualified officer reviews and records the official disposition.
The four proposed categories are High Risk, Moderate Risk, Low Risk, and No Identified Exposure. They are operational triage labels only. The classification engine must be transparent, versioned, configurable and approved by the Ministry’s public-health authority.
2. Background and Problem Statement
During an infectious-disease public-health event, authorities may need a consistent way to collect travel history, exposure information and symptom declarations from arriving travellers. Paper forms and disconnected spreadsheets can lead to incomplete information, slow retrieval, duplicated records and limited visibility of follow-up needs.
The proposed system addresses these operational challenges by providing a standardised digital declaration, a unique QR-based record lookup, role-controlled access and a central dashboard. It is designed to support—not replace—airport screening procedures, clinical assessment, laboratory processes and national surveillance systems.
3. Aim, Objectives and Scope
3.1 Aim
To design and implement a secure web-based traveller screening and QR verification platform that supports the collection, retrieval, review and management of traveller declarations relevant to Ebola exposure.
3.2 Objectives
Provide a responsive traveller form divided into logical sections with clear instructions and validation.
Capture identity, contact, itinerary, exposure, occupational, environmental and symptom information.
Calculate the 21-day look-back period and time since the last reported possible exposure using clearly defined dates.
Apply a Ministry-approved, version-controlled rule set to generate a preliminary screening category.
Generate a unique QR code that references a record without exposing personal or health information in the QR payload.
Allow authorised airport officers to scan and retrieve records securely.
Provide an authority dashboard for review, escalation, follow-up, configuration and audit.
Support configurable affected countries, subnational areas, dates and outbreak-specific rules.
Maintain confidentiality, integrity, availability and traceability of sensitive health information.
3.3 In Scope
Traveller registration and declaration submission.
Personal information and travel itinerary for the relevant 21-day look-back period.
Exposure history, healthcare/occupational exposure and animal/environmental exposure.
Symptom declaration and testing history.
Automated date calculations and preliminary risk triage.
QR generation, image download/save, and authenticated scanning.
Officer review, status updates, alerts, notes, follow-up tasks and reporting.
Administrator management of users, roles, affected areas, rule versions and system settings.
3.4 Out of Scope for the Initial Release
Diagnosing Ebola or interpreting laboratory results as a diagnostic authority.
Replacing national case investigation, contact tracing, isolation, treatment or referral protocols.
Automatically granting or refusing entry, imposing quarantine, or issuing travel clearance.
Direct integration with airline reservation systems, immigration systems or laboratory information systems unless separately approved.
Publicly exposing traveller records or allowing QR scans without authentication.
4. Stakeholders and User Roles
Role
Main responsibilities
Access level
Traveller
Complete declaration, review submission summary, view/save QR code, update only where policy permits.
Own submission only; no access to other records.
Airport screening officer
Authenticate, scan QR, view permitted screening summary, record screening outcome and refer cases.
Limited operational view; no unrestricted export.
Surveillance/public-health officer
Review exposure details, assess risk, record official decision, assign monitoring and follow-up.
Authorised health-record access based on jurisdiction and role.
System administrator
Manage users, roles, configuration, affected areas, form options and rule-set versions.
Administrative access; health-record access only if separately authorised.
Public-health supervisor
Approve rules, review escalations, monitor workload and reports.
Supervisory access and approval permissions.
Auditor/data-protection officer
Review access logs, policy compliance, retention and data handling.
Read-only audit access to approved logs and metadata.
Use least-privilege access. System administration and clinical/public-health decision authority should be separate roles wherever practical.
5. System Overview and Four Operational Phases
Phase 1 – Traveller Form Filling
The traveller opens the public screening portal, reads a privacy notice and completes the seven-section declaration. The interface should support saving a draft securely if the Ministry approves this feature, but an incomplete draft must not receive a final QR confirmation. The system validates required fields and displays a review page before submission.
Phase 2 – QR Code Generation
After submission, the backend creates a cryptographically random opaque token, stores a hash of that token against the traveller record, and generates a QR code containing a verification URL or signed opaque reference. The confirmation page displays the traveller’s name, submission reference, date/time, preliminary category and QR code. The QR image can be downloaded as PNG. On mobile, the user can save the image using the browser/device save flow or take a screenshot.
Phase 3 – Airport QR Scanning
An officer signs in through the staff portal and opens the scanner. The scanner requests camera permission and reads the QR token. The browser sends the token over HTTPS to the backend. The backend validates the token, checks revocation/expiry and officer permissions, then returns only the information that officer is authorised to view.
Phase 4 – Authorities’ Traveller Information Page
The authorised record page presents identity confirmation, travel itinerary, exposure answers, symptom declarations, the calculated timeline, the preliminary system category, rule-set version, and outstanding flags. Officers can record an assessment, refer the traveller, add a note, assign follow-up or escalate the case. All actions are timestamped and attributable to a named user.
Phase
Primary screen
System output
1. Traveller declaration
Responsive multi-section form
Validated declaration record
2. QR confirmation
Traveller confirmation page
Unique QR image and submission reference
3. QR scanning
Authenticated staff scanner
Secure record lookup
4. Authority record
Traveller detail and review page
Officer disposition, referral and follow-up record
6. Functional Requirements
ID
Requirement
FR-01
The system shall allow a traveller to start and submit a screening declaration.
FR-02
The form shall be divided into the seven sections defined in this document.
FR-03
Country fields shall use a maintained alphabetical list of countries and territories approved by the Ministry.
FR-04
The system shall support multiple itinerary entries, each with entry/departure dates and location details.
FR-05
For each exposure question answered Yes, the interface shall display relevant follow-up fields.
FR-06
The system shall calculate itinerary duration and days since last possible exposure.
FR-07
The system shall evaluate configured outbreak areas and rule versions to produce a preliminary category.
FR-08
The system shall generate a unique QR code after successful submission.
FR-09
The QR payload shall not contain name, date of birth, nationality, symptoms or other personal data.
FR-10
Only authenticated and authorised staff shall scan and retrieve protected traveller records.
FR-11
The officer record page shall display the information needed for screening and review.
FR-12
The system shall allow authorised officers to record a human-reviewed outcome and referral.
FR-13
The system shall maintain a tamper-evident audit trail of access and changes.
FR-14
Administrators shall manage affected countries/areas, effective dates, form options and rule versions.
FR-15
The system shall support record search by permitted identifiers and filters.
FR-16
The system shall support controlled export of approved operational reports.
FR-17
The system shall support QR revocation and reissue when a record is corrected or compromised.
FR-18
The system shall distinguish preliminary automated triage from the authorised officer’s final assessment.
7. Traveller Screening Form Specification
The form should use progressive sections, a visible completion indicator, plain-language help text, keyboard-accessible controls and clear validation messages. Required fields should be limited to information necessary for the approved screening purpose. Avoid collecting unnecessary sensitive information.
7.1 Section 1 – Traveller Personal Information
Field
Input / validation
Notes
Full name
Text; required
As shown on travel document. Store given and family names separately if needed.
Date of birth
Date; required
Do not ask for age as a separate source of truth.
Age
Calculated
Calculate from date of birth on the relevant date; display read-only.
Sex
Dropdown / options approved by Ministry
Use the Ministry-approved wording and allow an appropriate response option if required.
Nationality
Searchable dropdown
Alphabetical list from a maintained country/territory reference table; not hardcoded in page code.
Passport or travel document number
Text; policy decision
Collect only if necessary; encrypt or tightly restrict access.
Issuing country
Country dropdown
Use same maintained reference list.
Phone number
International phone input
Include country code; validate format, not ownership.
Email address
Email; optional/required by policy
For confirmation and follow-up if available.
Country of residence
Country dropdown
Separate from nationality.
Address / intended address in The Gambia
Text; policy decision
Collect only where operationally necessary.
Flight number
Text
Allow airline code and flight number.
Airline
Dropdown/text
Optional if flight number is sufficient.
Arrival airport
Dropdown
Configure approved entry points.
Date and time of arrival
Date/time
Store with timezone; standardise backend storage to UTC.
The original request includes both date of birth and age. Age should be calculated from date of birth to avoid inconsistent entries. The country list should be loaded from a maintained reference dataset and updated under change control.
7.2 Section 2 – Traveller Itinerary and Country History
Field
Input type
Business rule
Date of departure from country of residence
Date
Must not be after arrival date; validate against itinerary.
Countries visited in the last 21 days
Multiple selection
Use configurable country/area reference data.
Date of entry into each country
Date per itinerary row
One row per country/visit.
Date of departure from each country
Date per itinerary row
Must be on or after entry date.
City, region or district visited
Text / location selector
Allow multiple locations per visit.
Duration of stay
Calculated
Departure date minus entry date; define inclusive-day display consistently.
Purpose of visit
Dropdown
Tourism, Business, Employment, Education, Medical treatment, Family visit, Humanitarian work, Other.
Did you transit through another country?
Yes/No
If Yes, show transit-country details.
Airport or border crossing used
Text
Capture airport/border name and country.
Did you leave the transit airport?
Yes/No/Not applicable
Show only when transit is Yes.
Accommodation type
Dropdown
Hotel, guesthouse, private residence, healthcare facility, other; configure options.
Did you stay with local residents?
Yes/No/Unsure
If Yes, optional details subject to data minimisation.
The system should allow multiple itinerary rows, including repeated visits to the same country. It must compare travel dates against the configured look-back window relative to the traveller’s arrival date. A trip through an affected country does not automatically establish exposure.
7.3 Section 3 – Exposure to Suspected or Confirmed Ebola Cases
Question
Answer options
Direct physical contact with anyone diagnosed with Ebola
Yes / No / Unsure
Cared for someone suspected of having Ebola
Yes / No / Unsure
Lived with someone who had symptoms consistent with Ebola
Yes / No / Unsure
Touched blood or bodily fluids of a suspected or confirmed case
Yes / No / Unsure
Handled contaminated clothing, bedding or medical equipment
Yes / No / Unsure
Shared a household with a confirmed Ebola patient
Yes / No / Unsure
Unprotected sexual contact with an Ebola survivor
Yes / No / Unsure
Exposed to a dead body suspected of Ebola infection
Yes / No / Unsure
Attended a funeral involving someone suspected or confirmed to have Ebola
Yes / No / Unsure
For each Yes response, display a repeatable exposure-detail panel. For Unsure responses, display a clarification panel and flag for human review; do not silently treat Unsure as No.
Follow-up field
Input / notes
Date/time of exposure
Date/time; allow approximate date and mark it as estimated.
Location of exposure
Country, region/district, city and free-text detail.
Duration of contact
Numeric duration plus unit, or estimated range.
Type of contact
Dropdown plus details: physical contact, body fluids, caregiving, household, funeral/burial, contaminated material, sexual exposure, other.
Was PPE used?
Yes / No / Unsure / Not applicable.
PPE type and adequacy
Select PPE items and whether use followed approved protocol; expert review required.
Was there PPE failure or accidental exposure?
Yes / No / Unsure; if Yes, describe route and circumstances.
Was the person subsequently confirmed to have Ebola?
Yes / No / Unknown / Pending.
Source of information
Traveller report / official notification / other; optional.
The application should support more than one exposure event per traveller. Each event should have its own date, location, contact type and assessment status.
7.4 Section 4 – Healthcare Facility and Occupational Exposure
Question
Answer / conditional detail
Visited a hospital or healthcare facility in an outbreak-affected area?
Yes / No / Unsure; if Yes, facility, location, dates and reason.
Worked in an Ebola treatment centre?
Yes / No / Unsure; if Yes, role, dates, PPE and tasks.
Are you a healthcare worker?
Yes / No; occupation/role if Yes.
Handled laboratory samples from suspected Ebola patients?
Yes / No / Unsure; sample type, facility, date, containment/PPE and incident details.
Cleaned rooms or equipment used by suspected Ebola patients?
Yes / No / Unsure; task, date, PPE and any failure.
Participated in burial or mortuary activities?
Yes / No / Unsure; role, direct contact and PPE details.
Needle-stick injury involving potentially contaminated material?
Yes / No / Unsure; date, location, material and immediate response.
Capture facility name, facility type, location, date range and activity. A hospital visit alone must not automatically result in High Risk. The nature of contact, patient area, PPE, incident details and applicable public-health rules must be assessed.
7.5 Section 5 – Animal and Environmental Exposure
Question
Answer / conditional detail
Handled bats or non-human primates in an affected area?
Yes / No / Unsure; species if known, date, location and contact type.
Touched a dead wild animal?
Yes / No / Unsure; animal type, date and location.
Handled raw bushmeat?
Yes / No / Unsure; animal type, preparation/cooking status and date.
Handled blood or bodily fluids from potentially infected wildlife?
Yes / No / Unsure; material, route and PPE.
Entered caves or mines inhabited by bats?
Yes / No / Unsure; location, date and activity.
The relevance of wildlife questions must be configurable for the outbreak strain and current epidemiological assessment. A Yes answer should trigger review under the approved rule set; it should not automatically be assigned a category without context.
7.6 Section 6 – Current Health Condition and Symptoms
Symptom / field
Input type / notes
Fever or history of fever
Yes / No; capture onset, highest known temperature and resolved/current status.
Severe headache
Yes / No
Muscle or joint pain
Yes / No
Extreme tiredness
Yes / No
Sore throat
Yes / No
Vomiting
Yes / No
Diarrhoea
Yes / No
Abdominal pain
Yes / No
Unexplained bleeding
Yes / No; urgent clinical escalation according to protocol.
Unusual bruising
Yes / No
Skin rash
Yes / No
Current body temperature (°C)
Numeric; optional, with measurement date/time and method.
Date symptoms started
Date; allow approximate date.
Are symptoms still present?
Yes / No / Unsure
Have symptoms worsened?
Yes / No / Unsure
Have you received medical attention?
Yes / No; if Yes, facility/date.
Have you undergone Ebola testing?
Yes / No / Pending
Test result and date
Only if tested; result options and date, with source/verification status.
Symptoms are non-specific and cannot diagnose Ebola. A symptom report should prompt the Ministry-approved clinical screening/referral workflow. The interface must not tell a traveller that they have Ebola or that they are safe based only on the questionnaire.
7.7 Section 7 – Exposure Timeline
Field
How determined
First possible exposure
Earliest reported exposure event date; may be manually confirmed by officer.
Last possible exposure
Latest relevant reported exposure date; use event-level dates and uncertainty flags.
Date of arrival in The Gambia
From arrival details.
Days since last exposure
Arrival date minus last possible exposure date; display as a date-based calculation.
Within 21-day observation period?
Yes if arrival is within the configured 21-day period after last possible exposure; exact boundary must follow approved policy.
Monitoring end date
Last exposure date plus 21 days, subject to approved national guidance and event-specific rules.
The 21-day observation clock is anchored to the last possible exposure—not simply the date the traveller left an affected country. The system must retain the underlying dates and calculation timestamp. If the exposure date is unknown or approximate, the system must flag the timeline for manual review rather than presenting a false precision.
Date calculations must define whether the arrival day is day 0 or day 1 and whether the observation period ends at the start or end of the calculated date. The Ministry’s approved protocol must determine this boundary.
8. Risk Classification and Decision Support
The system generates a preliminary triage category using a configurable, version-controlled rules engine. The result is an aid to authorised staff and must always show the reasons and relevant answers that contributed to the category. The Ministry must approve the exact decision table before deployment.
8.1 Proposed Categories
Category
Indicative interpretation
System workflow
High Risk
Credible high-risk exposure, such as unprotected direct contact with infectious body fluids, needlestick involving potentially infectious material, direct unprotected contact with a suspected/confirmed case, or other Ministry-defined high-risk event.
Urgent flag; immediate alert to designated surveillance/airport health officer; follow approved infection-prevention, clinical assessment and referral protocol. Do not delay urgent action pending form completion.
Moderate Risk
Potential, uncertain or incompletely characterised exposure requiring additional assessment; examples may include close contact with an acutely ill person of unknown status or work in a relevant facility with unclear exposure details.
Manual assessment queue; request clarification; notify surveillance team; monitoring or other actions only as directed by authorised officer.
Low Risk
A limited or protected contact where approved criteria indicate no significant exposure, but follow-up advice or monitoring may still be appropriate.
Record rationale; provide approved health information; follow monitoring guidance where directed; reassess if symptoms or new information arise.
No Identified Exposure
No relevant exposure identified under the current questionnaire and configured outbreak criteria. Travel through an affected country alone may not establish exposure.
Record assessment; provide approved health information and instructions for seeking care if symptoms develop.
8.2 High-Risk Rule Examples for Expert Approval
Direct, unprotected physical contact with a person confirmed or suspected to have Ebola while infectious, where the contact meets the approved exposure definition.
Direct contact of eyes, nose, mouth or broken skin with infectious blood or bodily fluids without appropriate protection.
Caring for an Ebola patient without appropriate PPE or with a relevant PPE breach.
Handling the body of a person who died from suspected or confirmed Ebola without appropriate protection.
Direct contact during a burial involving an infected body or bodily fluids without appropriate protection.
Needle-stick or other percutaneous injury involving potentially infectious material.
Unprotected sexual exposure involving an Ebola survivor where the approved survivor-clearance criteria have not been met.
These are examples for rule design, not a complete clinical definition. The Ministry’s infection prevention and control, surveillance and clinical experts must define the exact criteria, infectious periods, PPE adequacy and survivor-related requirements for the relevant outbreak.
8.3 Moderate-Risk Rule Examples
Visited a healthcare facility in an affected area without a clearly established high-risk contact.
Attended a funeral in an affected community without reported direct contact with the body.
Had close contact with an acutely ill person whose Ebola status is unknown.
Lived in an outbreak-affected community during the relevant period, where current guidance identifies this as requiring further assessment.
Worked in a facility where Ebola patients were treated, but the precise task, proximity or PPE circumstances are unclear.
Handled environmental cleaning or medical waste in a relevant facility where possible exposure cannot be excluded.
8.4 Low-Risk and No-Identified-Exposure Examples
Low Risk may include a contact assessed as limited and protected, with appropriate PPE and infection-control procedures, where the approved protocol finds no significant exposure. No Identified Exposure may apply where no relevant affected-area or case contact, contaminated-material, healthcare, occupational, burial or wildlife exposure is identified under the current rules. Travel through an affected country alone should not automatically produce a High or Moderate category.
8.5 Rule Precedence and Human Review
High-risk criteria take precedence when a credible qualifying exposure is present.
An Unsure answer, missing critical detail, conflicting dates or unverified information should create a manual-review flag; it must not be silently converted to No.
Symptoms requiring urgent clinical assessment should trigger the approved symptom pathway independently of the exposure category.
Moderate, Low and No Identified Exposure rules must be applied only after checking for higher-priority criteria.
Officers may override a preliminary category only with a reason, their identity, timestamp and applicable protocol reference.
Every assessment stores the rule-set version, input snapshot/reference, result, reasons and any officer override.
8.6 Illustrative Decision Logic (Not a Clinical Protocol)
The following is an implementation pattern only. The final conditions and precedence must be supplied and signed off by the Ministry.
if urgent_symptom_trigger:    create_urgent_clinical_review_flag()if credible_high_risk_exposure_under_approved_rules:    preliminary_category = "HIGH"elif possible_or_uncertain_exposure:    preliminary_category = "MODERATE"elif limited_or_protected_exposure_meets_low_risk_rules:    preliminary_category = "LOW"elif no_relevant_exposure_identified:    preliminary_category = "NO_IDENTIFIED_EXPOSURE"else:    preliminary_category = "MANUAL_REVIEW"store(rule_set_version, reasons, calculated_dates, timestamp)require_authorised_officer_review_when_policy_requires()
8.7 Explainability
The result page should show a concise reason list, for example: “Moderate – reported visit to a healthcare facility in a configured affected area; no direct bodily-fluid contact reported; officer review required.” It must also show the configuration and rule-set version used. Avoid opaque scores unless a validated, approved scoring method exists.
9. QR Code Design and Verification
9.1 QR Payload
The QR code should contain a random, high-entropy opaque token or a signed reference URL. It must not embed a JSON record containing the traveller’s name, date of birth, passport number, symptoms, exposure history or risk category. A QR image can be photographed or forwarded, so the payload must be treated as a bearer reference and protected accordingly.
9.2 Recommended Workflow
After successful submission, generate at least 128 bits of cryptographically secure random token material.
Store only a secure hash of the token in the database; associate it with the traveller record and status.
Encode a HTTPS verification URL containing the opaque token, not personal data.
Require staff authentication before returning any protected record details.
Check token status, expiry/revocation and officer permissions on every lookup.
Rate-limit failed lookups and log scan attempts without logging the raw token.
Allow an authorised user to revoke and reissue a QR code if the traveller record is corrected or the code is compromised.
9.3 Traveller QR Confirmation Page
Display traveller’s full name as entered in the form.
Display submission reference and submission date/time.
Display the QR code at a size suitable for mobile scanning.
Provide a “Download QR Code” action that saves a PNG image where supported.
Explain that a screenshot may be used as a backup, but the code must remain readable.
Provide a clear instruction to present the code to authorised airport health personnel.
Do not present the preliminary category as a diagnosis or travel clearance.
9.4 QR Expiry and Reuse
The Ministry should define token validity. Options include expiry after arrival processing, a defined short period after arrival, or validity until explicitly revoked. The token should not be reusable as a general public lookup link. Staff authentication and audit logging remain mandatory regardless of expiry.
10. Authority Dashboard and Case Workflow
10.1 Dashboard Overview
Summary cards: submissions today, awaiting review, urgent flags, records scanned, follow-ups due.
Queue filters: category, arrival date, airport, review status, exposure window and assigned officer.
Search by submission reference and other approved identifiers.
Alerts for high-risk flags, urgent symptom declarations, missing critical information and approaching follow-up deadlines.
Configuration panel for authorised administrators, separated from routine case management.
10.2 Traveller Record Page
Panel
Information displayed
Identity
Name, date of birth/age, nationality, flight details and submission reference.
Itinerary
Countries/areas visited, dates, locations, transit and accommodation details.
Exposure history
Each reported event, contact type, date, location, PPE and confirmation status.
Healthcare/occupational
Facility, activity, dates, role and incident details.
Animal/environmental
Wildlife or environmental contact details relevant to configured rules.
Symptoms/testing
Reported symptoms, onset, current status, temperature and reported testing information.
Timeline
First/last possible exposure, days elapsed, 21-day window and uncertainty flags.
Assessment
Preliminary category, rule version, reasons, review status and officer decision.
Actions
Refer, escalate, assign follow-up, add note, update status, revoke/reissue QR where authorised.
10.3 Case Statuses
Status
Meaning
Submitted
Traveller declaration received; initial automated processing completed.
Awaiting review
Manual assessment required or review pending.
Urgent review
High-priority flag requiring immediate action under approved protocol.
Officer assessed
Authorised officer has recorded an assessment.
Referred
Traveller has been referred through an approved pathway.
Monitoring/follow-up
Follow-up task or monitoring has been assigned.
Closed
Authorised officer has closed the record with a reason.
Cancelled/duplicate
Record invalidated or merged under an auditable process.
10.4 Officer Actions
Officers should be able to record assessment outcome, rationale, referral destination, date/time, assigned team, follow-up due date and contact attempts. Changes to the preliminary category must never erase the original automated result. The audit history must preserve both.
11. System Architecture and Technology Stack
A three-tier web architecture is recommended: browser-based frontend, Python application/API backend, and MySQL relational database. A separate background task component may handle notifications and scheduled jobs.
Layer
Recommended technology
Responsibilities
Frontend
HTML5, CSS3, JavaScript
Traveller form, validation, dynamic questions, QR display, staff dashboard and camera-based scanner.
Backend/API
Python with Django or Flask
Authentication, authorisation, business rules, validation, QR generation, API endpoints, audit events and reporting.
Database
MySQL 8.x
Traveller records, itinerary, exposures, symptoms, users, roles, rule versions, QR token hashes and audit logs.
QR generation
Python QR library (e.g. qrcode)
Create QR image containing opaque verification reference.
Scanner
Browser camera API with maintained JS QR library
Read QR code on supported mobile/desktop devices; send token to backend.
Deployment
Linux server, reverse proxy, WSGI server
HTTPS termination, application hosting, backups, monitoring and access controls.
11.1 High-Level Architecture
TRAVELLER / STAFF BROWSER        |        | HTTPS        vWEB FRONTEND (HTML + CSS + JavaScript)        |        | authenticated API requests        vPYTHON APPLICATION / REST API  |        |          |          |  |        |          |          +-- Audit & notification service  |        |          +------------- Configurable rules engine  |        +------------------------ QR token service  +--------------------------------- Authentication & permissions        |        vMYSQL DATABASE  - Traveller and contact records  - Itinerary and exposure events  - Symptoms and timeline  - Assessment and rule versions  - Users, roles and audit events
11.2 Suggested Backend Modules
accounts: staff accounts, authentication, role-based permissions and session management.
travellers: traveller profile and declaration lifecycle.
itineraries: countries, areas, transit and accommodation records.
exposures: case contact, healthcare, occupational, burial and environmental events.
symptoms: symptom declarations and reported testing details.
assessment: configurable rules, calculations, reasons and officer review.
qr_verification: token generation, hashing, revocation, expiry and scan lookup.
administration: outbreak areas, country reference data, dropdown options and rule approvals.
reporting: authorised dashboard metrics and exports.
audit: immutable-style event history and security monitoring.
12. Database Design
Use relational tables with primary keys, foreign keys, timestamps and appropriate indexes. Store dates as DATE and event timestamps as DATETIME/TIMESTAMP with a documented timezone strategy. Use UTC for backend timestamps and preserve the local time zone where operationally required.
12.1 Proposed Core Tables
Table
Example columns
Purpose
users
id, full_name, username/email, password_hash, role_id, status, last_login_at, created_at
Staff accounts.
roles
id, role_name, permissions_json or linked permission records
Role-based access.
travellers
id, full_name, date_of_birth, sex, nationality_code, residence_country_code, phone, email, document_number_encrypted
Identity and contact information.
submissions
id, traveller_id, reference_code, flight_number, airline, arrival_airport, arrival_at, submitted_at, status, rule_set_id
One screening submission per journey/declaration.
country_reference
iso_code, country_name, active
Alphabetical maintained country/territory list.
outbreak_areas
id, country_code, region_name, district_name, status, valid_from, valid_to, source_reference, approved_by
Configurable affected areas.
itinerary_entries
id, submission_id, country_code, entry_date, departure_date, city_region, purpose, accommodation_type, transit_flag, airport_crossing, left_transit_airport
One row per visit.
exposure_events
id, submission_id, exposure_type, answer, exposure_date, location, duration_value, duration_unit, contact_type, ppe_used, ppe_failure, source_status
Repeatable reported exposure events.
healthcare_events
id, submission_id, facility_name, facility_type, location, start_date, end_date, activity_type, ppe_details, incident_details
Healthcare and occupational exposure.
environmental_events
id, submission_id, event_type, animal_type, location, event_date, contact_details, ppe_details
Animal/environmental events.
symptom_reports
id, submission_id, symptom_code, present, onset_date, resolved, severity_notes
One row per symptom or symptom group.
health_assessments
id, submission_id, preliminary_category, reasons_json, rule_set_id, assessed_at, officer_id, officer_category, rationale, review_status
Automated and human assessment history.
timeline_calculations
id, submission_id, first_exposure_date, last_exposure_date, arrival_date, days_since_last_exposure, within_21_days, calculated_at
Derived timeline snapshot.
qr_tokens
id, submission_id, token_hash, issued_at, expires_at, revoked_at, status
QR token metadata; never store raw token.
follow_up_tasks
id, submission_id, assigned_to, task_type, due_at, status, outcome, created_by
Monitoring/referral tasks.
notifications
id, submission_id, recipient_role/user, event_type, sent_at, delivery_status
Alert delivery tracking.
rule_sets
id, version, name, effective_from, effective_to, status, approved_by, approved_at, change_summary
Versioned screening rules.
audit_logs
id, actor_user_id, action, entity_type, entity_id, timestamp, source_ip, metadata
Access and change history.
12.2 Relationships
One traveller may have multiple submissions over time.
One submission may have many itinerary entries, exposure events, healthcare events, environmental events and symptom reports.
One submission may have multiple assessment records as the case is reviewed or reassessed.
One submission may have one active QR token at a time, with historical tokens retained as revoked/expired records.
One rule set may be referenced by many assessments.
One user may create many audit events and may be assigned many follow-up tasks.
12.3 Data Modelling Recommendations
Use a unique internal UUID or integer primary key; never use passport number as the database primary key.
Use ISO country codes and a maintained reference table for countries.
Use lookup tables for controlled values where administrators need to manage options.
Encrypt highly sensitive identifiers at application or database-field level and restrict decryption permissions.
Store assessment reasons and rule-set version so decisions can be reconstructed.
Use soft deletion or status changes for operational records; preserve legally required audit history.
Index submission reference, arrival date, status, category, token hash and foreign keys.
Define retention and deletion rules with the Ministry and applicable Gambian law before production.
13. Data Validation and Business Rules
Rule area
Validation
Dates
Departure must not precede entry; exposure date cannot be in the future unless correcting an estimated value; arrival and itinerary dates must be logically consistent.
Look-back period
Itinerary questions should cover the 21 days before arrival, based on the Ministry-approved boundary and local date/time handling.
Age
Calculate from date of birth; do not accept an independently entered age as authoritative.
Conditional questions
Show exposure details when Yes; show clarification/manual-review prompt when Unsure; hide or mark not applicable when No.
Multiple events
Allow multiple itinerary and exposure records; do not force one country or one exposure only.
Symptoms
Capture onset/resolution and current status; do not infer a diagnosis.
Timeline
Calculate from last possible exposure, not departure from affected country.
Unknown dates
Preserve unknown/approximate status and trigger manual review where relevant.
QR
Generate only after successful submission; token must be unique, unguessable, revocable and not contain PII.
Category
Store preliminary category separately from officer-assessed category.
Configuration
Affected-area and rule changes must be versioned, approved and effective-dated.
14. Security, Privacy and Audit
The system will process identity, itinerary and health-related information. Treat all such data as sensitive and apply privacy-by-design principles. Obtain Ministry legal, data-protection and information-security review before collecting live traveller information.
14.1 Minimum Security Controls
HTTPS/TLS for all traffic; disable insecure HTTP access.
Strong staff authentication; multi-factor authentication for privileged roles where feasible.
Role-based and, where appropriate, location-based access control.
Secure password hashing using a modern password-hashing algorithm; never store plaintext passwords.
CSRF protection, output encoding, input validation, parameterised SQL/ORM queries and secure session cookies.
Rate limiting and abuse monitoring for QR lookup and login endpoints.
Encryption at rest for backups and sensitive fields; controlled key management.
Short-lived staff sessions, logout, account lockout/risk controls and access review.
Audit logging for record views, searches, scans, exports, edits, overrides and configuration changes.
Backups, restore testing, vulnerability management and security incident response.
Do not include personal or health data in QR payloads, URLs, analytics, error messages or application logs.
14.2 Privacy Controls
Display a clear privacy notice explaining purpose, data collected, access, retention and contact point.
Collect only information necessary for the approved public-health purpose.
Restrict record visibility to staff who need it for assigned duties.
Define a lawful basis and retention schedule with the Ministry’s legal and data-protection teams.
Provide a process for correcting inaccurate traveller information while preserving the audit trail.
Define handling for minors and travellers unable to complete the form, according to approved policy.
Do not use the data for unrelated purposes without proper legal authority and governance.
14.3 Audit Events
Log who accessed or changed a record, what action occurred, when it occurred, the affected record identifier, and relevant context. Do not log passwords, raw QR tokens or unnecessary health details. Audit records should be protected from ordinary editing and periodically reviewed.
15. Non-Functional Requirements
Requirement
Target / design expectation
Usability
Simple, mobile-first form; plain language; save-and-resume only if approved.
Accessibility
Aim for WCAG 2.2 AA; keyboard navigation, labels, contrast, focus states and screen-reader support.
Performance
Common form and record pages should load promptly under expected airport network conditions; define measurable service targets during discovery.
Availability
Deploy with monitored uptime, backups and a documented recovery plan appropriate to airport operations.
Scalability
Support concurrent submissions and scans across designated entry points; load-test realistic peak volumes.
Reliability
Prevent duplicate submissions where possible; make API operations safe to retry.
Maintainability
Modular backend, documented APIs, automated tests, configuration-driven rules and version control.
Compatibility
Current supported desktop and mobile browsers; scanner fallback for devices without camera access.
Interoperability
Use documented REST APIs and standard country codes; integrations only after approval.
Auditability
Preserve assessment versions, officer decisions and access history.
Resilience
Provide a documented manual contingency process during outages.
16. User Interface and Accessibility
16.1 Traveller Interface
Landing page with purpose, eligibility/instructions, estimated completion time and privacy notice.
Progress indicator showing seven sections and completion state.
One section per screen or clearly separated panels; allow Back and Continue.
Repeatable cards for itinerary visits and exposure events.
Conditional follow-up questions displayed immediately after Yes/Unsure answers.
Review-before-submit page with edit links.
Confirmation page with name, submission reference and QR image.
Mobile-friendly buttons and clear error summaries.
16.2 Staff Interface
Secure staff login and role-aware navigation.
Large, accessible Scan QR action and manual reference lookup fallback.
Prominent but non-stigmatising status indicators with text labels, not colour alone.
Clear separation between system-generated triage and officer decision.
Record timeline, reasons, review notes and follow-up tasks in a readable layout.
Confirmation dialogs for sensitive actions such as override, revoke, export and close.
16.3 Camera and Save Behaviour
Camera scanning requires HTTPS and user permission. If permission is denied or the camera is unavailable, allow an authorised officer to enter a submission reference or use a supported image-upload scan flow if approved. The traveller QR page should provide a downloadable PNG; saving directly to a device photo library depends on browser and operating-system behaviour, so the interface should provide a standard download/share action and explain screenshot as a fallback.
17. Reports and Monitoring
Report
Possible measures
Access
Arrival screening summary
Submissions by date, airport, flight and processing status.
Supervisor / authorised officer
Triage workload
Preliminary categories, awaiting review, urgent flags, officer-assessed categories.
Surveillance supervisor
Exposure patterns
Aggregated exposure types, affected areas and dates; avoid unnecessary identifying detail.
Approved public-health analysts
Follow-up management
Tasks due, overdue, completed and assigned team.
Assigned officers / supervisors
System operations
Login failures, scan errors, response times, availability and queue failures.
System administrator / security
Audit report
Record access, edits, overrides, exports and configuration changes.
Auditor / authorised governance role
Reports should default to aggregate data. Exports containing identifiable records require explicit permissions, a recorded purpose and audit logging.
18. Testing and Quality Assurance
18.1 Testing Types
Unit testing: date calculations, validation, QR token generation and individual rules.
Integration testing: frontend/API/database, QR scan lookup, alerts and user permissions.
End-to-end testing: traveller completes form → receives QR → officer scans → officer reviews record.
Security testing: authentication, authorisation, injection, CSRF, session handling, token guessing and rate limits.
Usability testing: travellers with different devices and levels of digital literacy.
Accessibility testing: keyboard-only, screen reader, contrast and form error handling.
Performance testing: concurrent traveller submissions and airport scanning workload.
Backup/restore and disaster-recovery testing.
Public-health validation: scenario-based review by designated experts against approved national guidance.
18.2 Critical Test Scenarios
Scenario
Expected system behaviour
Traveller reports no relevant exposure and no symptoms
Apply current approved rules; show preliminary result and advice; do not imply guaranteed absence of infection.
Traveller reports credible high-risk exposure
Flag urgent review and notify designated staff according to approved workflow.
Traveller answers Unsure to a key exposure question
Flag for manual clarification; do not silently treat as No.
Traveller visited a hospital but reports no direct exposure
Do not automatically assign High Risk; evaluate details under approved rules.
Last exposure is within the observation period
Calculate from last exposure date and show monitoring-window status.
Last exposure date is unknown
Mark timeline uncertain and require review.
QR token is revoked or expired
Do not reveal protected record; show controlled error and log attempt.
Unauthorised user scans a valid QR
Require authentication/deny access; do not disclose traveller information.
Rule set changes after submission
Preserve original rule version; reassessment under new rules must create a new assessment record.
Officer overrides preliminary category
Require reason; preserve original category and log officer identity/time.
18.3 Acceptance Testing
Before launch, the Ministry should approve user-acceptance scenarios, verify all four operational phases, validate the rule set with experts, confirm privacy/security controls, test airport network conditions and sign off operating procedures.
19. Deployment and Operations
19.1 Environments
Environment
Purpose
Development
Developer work and automated tests using synthetic data only.
Testing/UAT
Ministry review, integration tests and user acceptance using synthetic or properly controlled test data.
Production
Live environment with approved access, monitoring, backups and incident response.
19.2 Deployment Components
Linux server or approved government hosting environment.
Reverse proxy such as Nginx with HTTPS certificates.
Python application served by a production WSGI server.
MySQL database on a private network, not directly exposed to the internet.
Environment-based secrets and configuration; no credentials committed to source control.
Centralised monitoring, alerting, log retention and backup jobs.
Documented release, rollback and database migration procedures.
19.3 Operational Continuity
Prepare an approved paper/manual contingency workflow for internet, power, server or camera outages. Define how records captured during downtime are reconciled, who may enter them, how duplicates are resolved and how the audit trail is preserved. Do not let a QR scan failure be interpreted as a negative screening result.
20. Development Plan and Deliverables
Stage
Activities
Deliverables
1. Discovery and approval
Confirm use cases, legal basis, stakeholders, form content, public-health rules, referral process and data governance.
Approved requirements, workflow maps, risk-rule specification and privacy requirements.
2. UX and data design
Wireframes, form logic, role matrix, ERD and API design.
UI prototype, database schema and API specification.
3. Core development
Build authentication, traveller form, data validation and MySQL persistence.
Working traveller submission module.
4. QR and scanning
Implement opaque token lifecycle, QR page and staff scanner.
QR generation and authenticated lookup.
5. Assessment and dashboard
Implement approved rules engine, review queues, officer actions, alerts and reporting.
Authority dashboard and case workflow.
6. Security and testing
Threat modelling, access tests, performance, accessibility, UAT and public-health scenario validation.
Test report, security findings and resolved defects.
7. Pilot and rollout
Pilot at approved entry point, train users, monitor and refine.
Training materials, pilot report, operational handover.
20.1 Suggested Minimum Viable Product
For a first controlled pilot, prioritise: the seven-section form; secure submission; country/affected-area configuration; rule-version recording; QR generation; authenticated staff scanning; record detail page; manual officer assessment; audit logging; and a basic dashboard. Advanced integrations, automated messaging and analytics can follow after governance approval.
21. Risks, Assumptions and Dependencies
Risk / dependency
Mitigation
Outdated outbreak locations or rules
Effective-dated configuration, named approver, review schedule and version history.
Incorrect automated classification
Expert-approved rule set, transparent reasons, manual review and continuous validation.
Exposure answers incomplete or misunderstood
Plain language, examples, Unsure option, conditional follow-ups and officer clarification.
QR code copied or misused
Opaque high-entropy token, staff authentication, expiry/revocation, rate limiting and audit.
Sensitive information disclosed
Least privilege, encryption, privacy notice, staff training and monitoring.
Network or power outage at airport
Offline contingency procedure and controlled reconciliation.
False confidence from a No Identified Exposure result
Clear wording that screening is not diagnosis or a guarantee of no infection.
Country/area list becomes stale
Administrator configuration backed by authoritative Ministry sources.
Scope expands beyond initial delivery
Approved MVP, change-control process and prioritised backlog.
Legal or regulatory requirements unclear
Ministry legal, data-protection and information-security review before production.
21.1 Key Assumptions
The Ministry will designate a public-health owner responsible for approving the form and rules.
The Ministry will identify authorised entry points, staff roles and referral contacts.
An approved country/territory reference list and authoritative outbreak-area information source will be available.
Hosting, data residency, retention and lawful processing requirements will be determined before production.
Travellers will have access to a device and connectivity, or an assisted/manual process will be available.
22. Acceptance Criteria
A traveller can complete all seven sections on a supported mobile and desktop browser.
Country selection is searchable and alphabetically ordered from maintained reference data.
Multiple itinerary entries and exposure events can be added and edited before submission.
Yes and Unsure answers trigger the appropriate follow-up and review logic.
Duration, age and exposure timeline calculations pass approved boundary tests.
The classification engine uses a Ministry-approved, versioned configuration and displays reasons.
A QR code is generated only after successful submission and contains no personal or health information.
The traveller confirmation page displays the traveller’s name and provides a QR download option.
An authenticated authorised officer can scan a QR and retrieve the correct record.
Unauthorised users cannot retrieve protected records by scanning or guessing a token.
Officer decisions, overrides, referrals and access are recorded in audit history.
Administrators can update affected areas and rule versions without changing application source code.
Security, privacy, backup, accessibility and user-acceptance checks are signed off before live deployment.
Appendix A – Suggested API Endpoints
Method and endpoint
Purpose
Access
POST /api/v1/submissions
Create traveller submission after validation.
Public, rate-limited
GET /api/v1/submissions/{reference}/confirmation
Retrieve limited confirmation data.
Traveller-specific secure access or one-time flow
GET /api/v1/qr/verify/{token}
Resolve QR token to protected record.
Authenticated staff only
POST /api/v1/qr/{id}/revoke
Revoke token.
Authorised officer/admin
GET /api/v1/staff/dashboard
Dashboard summary.
Staff roles
GET /api/v1/staff/submissions/{id}
Retrieve permitted traveller record.
Permission-checked staff
POST /api/v1/staff/submissions/{id}/assessment
Record officer assessment.
Authorised public-health officer
POST /api/v1/staff/submissions/{id}/referrals
Create referral record.
Authorised officer
POST /api/v1/admin/outbreak-areas
Create/update affected area.
Administrator with approval permission
POST /api/v1/admin/rule-sets
Create and submit rule-set version.
Rule administrator; approval separate
POST /api/v1/admin/rule-sets/{id}/approve
Approve rule-set version.
Designated public-health approver
Endpoint names are illustrative. The final API specification should define request/response schemas, authentication, permissions, validation errors, idempotency, rate limits and audit behaviour.
Appendix B – Suggested Project Folder Structure
ebola-traveller-screening/├── backend/│   ├── config/│   ├── accounts/│   ├── travellers/│   ├── itineraries/│   ├── exposures/│   ├── symptoms/│   ├── assessment/│   ├── qr_verification/│   ├── administration/│   ├── reporting/│   ├── audit/│   └── manage.py├── frontend/│   ├── assets/│   │   ├── css/│   │   ├── js/│   │   └── images/│   ├── traveller/│   └── staff/├── database/│   ├── migrations/│   ├── seed/│   └── schema/├── tests/├── deployment/├── documentation/└── README.md
Appendix C – Recommended Form Design Principles
Use clear, non-alarming language and explain why each section is being asked.
Provide an Unsure option for questions where a traveller may not know the answer.
Do not preselect No for exposure or symptom questions.
Allow multiple events and dates rather than compressing complex histories into one text box.
Use accessible date controls and display dates in an unambiguous format.
Clearly distinguish required fields from optional fields.
Provide a final review page and a confirmation reference after successful submission.
Ensure the traveller can ask for assistance without being penalised by the interface.
Appendix D – Items Requiring Ministry Approval Before Development Goes Live
Final questionnaire wording and required/optional fields.
National case definitions, exposure definitions and outbreak-specific risk categories.
21-day look-back and observation-period boundary calculations.
Relevant affected countries, regions, districts and effective dates.
PPE adequacy criteria, sexual exposure/survivor criteria and wildlife exposure relevance.
Symptom triggers and urgent referral/infection-control pathways.
Whether and how laboratory test results may be recorded or verified.
Data controller/processor responsibilities, lawful basis, privacy notice and retention period.
Hosting location, data residency, access review and breach response requirements.
QR validity, traveller correction process and assisted/manual screening workflow.
Officer roles, escalation contacts, operating hours and contingency procedures.
Conclusion
The proposed system provides a structured digital process for traveller declarations, QR-based record retrieval and public-health review. Its success depends not only on software implementation but also on approved epidemiological rules, clear operational ownership, staff training, privacy safeguards and reliable airport procedures. The recommended approach is to build a secure minimum viable product, validate it with Ministry public-health experts, pilot it in a controlled environment and expand only after formal approval.
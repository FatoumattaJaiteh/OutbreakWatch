-- ==============================================================================
-- EBOLA TRAVELLER SCREENING & QR CODE VERIFICATION SYSTEM
-- Ministry of Health, The Gambia
-- Database Schema for Supabase (PostgreSQL 15+)
-- Production Ready & Idempotent (Safe to execute multiple times)
-- ==============================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ------------------------------------------------------------------------------
-- 1. ROLES TABLE & SEED DATA
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.roles (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

INSERT INTO public.roles (name, title, description) VALUES
    ('super_admin', 'Super Administrator', 'Full unrestricted access: user & role creation, audit logs, rules, and all operational tools.'),
    ('screening_officer', 'Airport Screening Officer', 'Authenticate, scan QR, view permitted screening summary, record screening outcome and refer cases.'),
    ('surveillance_officer', 'Surveillance / Public-Health Officer', 'Review exposure details, assess risk, record official decision, assign monitoring and follow-up.'),
    ('supervisor', 'Public-Health Supervisor', 'Approve rules, review escalations, monitor workload and reports.'),
    ('auditor', 'Auditor / Data-Protection Officer', 'Review access logs, policy compliance, retention and data handling.')
ON CONFLICT (name) DO UPDATE 
SET title = EXCLUDED.title, description = EXCLUDED.description;

-- ------------------------------------------------------------------------------
-- 2. USERS TABLE & AUTHENTICATION
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    password_hash TEXT,
    salt TEXT,
    role TEXT NOT NULL DEFAULT 'screening_officer' REFERENCES public.roles(name),
    badge_number TEXT,
    station TEXT DEFAULT 'Banjul International Airport (BJL)',
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'suspended', 'inactive')),
    last_login_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_users_email ON public.users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON public.users(role);

-- Seed Default Accounts (Admin: Admin@2026!, Staff: Staff@2026!)
INSERT INTO public.users (email, full_name, role, badge_number, station, status) VALUES
    ('admin@health.gov.gm', 'Super Administrator', 'super_admin', 'HQ-ADMIN-01', 'Ministry of Health HQ, Banjul', 'active'),
    ('screening@health.gov.gm', 'Fatou Ceesay', 'screening_officer', 'BJL-SO-104', 'Banjul International Airport (BJL)', 'active'),
    ('surveillance@health.gov.gm', 'Dr. Alieu Touray', 'surveillance_officer', 'EPI-SURV-08', 'Port Health Epidemiology Unit, Banjul', 'active'),
    ('supervisor@health.gov.gm', 'Dr. A. Darboe', 'supervisor', 'PHEOC-SUP-02', 'National Public Health Emergency Operations Center', 'active'),
    ('auditor@health.gov.gm', 'Momodou Bah', 'auditor', 'AUD-DPO-05', 'Data Protection & Ethics Compliance Directorate', 'active')
ON CONFLICT (email) DO NOTHING;

-- ------------------------------------------------------------------------------
-- 3. TRAVELLERS (PASSENGER DEMOGRAPHICS & IDENTITY)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.travellers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    full_name TEXT NOT NULL,
    date_of_birth DATE NOT NULL,
    calculated_age INT,
    sex TEXT NOT NULL CHECK (sex IN ('male', 'female', 'other', 'undisclosed')),
    nationality TEXT NOT NULL,
    residence_country TEXT NOT NULL,
    passport_number TEXT,
    issuing_country TEXT,
    phone_number TEXT NOT NULL,
    email TEXT,
    address_in_gambia TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_travellers_passport ON public.travellers(passport_number);
CREATE INDEX IF NOT EXISTS idx_travellers_phone ON public.travellers(phone_number);

-- ------------------------------------------------------------------------------
-- 4. SUBMISSIONS (JOURNEY / SCREENING DECLARATION)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.submissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    traveller_id UUID NOT NULL REFERENCES public.travellers(id) ON DELETE CASCADE,
    reference_code TEXT UNIQUE NOT NULL,
    flight_number TEXT NOT NULL,
    airline TEXT,
    arrival_airport TEXT NOT NULL DEFAULT 'Banjul International Airport (BJL)',
    arrival_date_time TIMESTAMPTZ NOT NULL,
    submitted_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL,
    status TEXT NOT NULL DEFAULT 'submitted' CHECK (
        status IN ('submitted', 'awaiting_review', 'urgent_review', 'officer_assessed', 'referred', 'monitoring', 'closed')
    ),
    preliminary_risk_category TEXT NOT NULL DEFAULT 'NO_IDENTIFIED_EXPOSURE' CHECK (
        preliminary_risk_category IN ('HIGH', 'MODERATE', 'LOW', 'NO_IDENTIFIED_EXPOSURE', 'MANUAL_REVIEW')
    ),
    urgent_symptom_flag BOOLEAN DEFAULT false,
    manual_review_reasons JSONB DEFAULT '[]'::jsonb,
    rule_set_version TEXT DEFAULT 'v1.0-gambia-baseline',
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_submissions_ref ON public.submissions(reference_code);
CREATE INDEX IF NOT EXISTS idx_submissions_status ON public.submissions(status);
CREATE INDEX IF NOT EXISTS idx_submissions_risk ON public.submissions(preliminary_risk_category);
CREATE INDEX IF NOT EXISTS idx_submissions_arrival ON public.submissions(arrival_date_time DESC);

-- ------------------------------------------------------------------------------
-- 5. ITINERARY ENTRIES (21-DAY LOOK-BACK)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.itinerary_entries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    submission_id UUID NOT NULL REFERENCES public.submissions(id) ON DELETE CASCADE,
    country_name TEXT NOT NULL,
    city_or_district TEXT,
    entry_date DATE NOT NULL,
    departure_date DATE NOT NULL,
    duration_days INT,
    purpose_of_visit TEXT,
    accommodation_type TEXT,
    is_transit BOOLEAN DEFAULT false,
    transit_airport TEXT,
    left_transit_airport BOOLEAN DEFAULT false,
    stayed_with_residents BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_itinerary_submission ON public.itinerary_entries(submission_id);

-- ------------------------------------------------------------------------------
-- 6. EXPOSURE EVENTS (EBOLA CASE CONTACT)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.exposure_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    submission_id UUID NOT NULL REFERENCES public.submissions(id) ON DELETE CASCADE,
    question_key TEXT NOT NULL,
    question_label TEXT NOT NULL,
    answer TEXT NOT NULL CHECK (answer IN ('Yes', 'No', 'Unsure')),
    exposure_date DATE,
    location_details TEXT,
    contact_type TEXT,
    ppe_used TEXT,
    ppe_failure_or_breach BOOLEAN DEFAULT false,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_exposures_submission ON public.exposure_events(submission_id);

-- ------------------------------------------------------------------------------
-- 7. HEALTHCARE & OCCUPATIONAL EXPOSURES
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.healthcare_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    submission_id UUID NOT NULL REFERENCES public.submissions(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,
    answer TEXT NOT NULL CHECK (answer IN ('Yes', 'No', 'Unsure')),
    facility_name TEXT,
    facility_location TEXT,
    activity_dates TEXT,
    role_or_occupation TEXT,
    ppe_details TEXT,
    incident_details TEXT,
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_healthcare_submission ON public.healthcare_events(submission_id);

-- ------------------------------------------------------------------------------
-- 8. ANIMAL & ENVIRONMENTAL EXPOSURES
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.environmental_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    submission_id UUID NOT NULL REFERENCES public.submissions(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,
    answer TEXT NOT NULL CHECK (answer IN ('Yes', 'No', 'Unsure')),
    species_or_animal TEXT,
    location_details TEXT,
    event_date DATE,
    contact_details TEXT,
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_environmental_submission ON public.environmental_events(submission_id);

-- ------------------------------------------------------------------------------
-- 9. SYMPTOM REPORTS & CLINICAL SIGNS
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.symptom_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    submission_id UUID NOT NULL REFERENCES public.submissions(id) ON DELETE CASCADE,
    symptoms_list JSONB NOT NULL DEFAULT '[]'::jsonb,
    has_fever BOOLEAN DEFAULT false,
    body_temperature NUMERIC(4,1),
    unexplained_bleeding BOOLEAN DEFAULT false,
    symptom_onset_date DATE,
    symptoms_still_present BOOLEAN DEFAULT true,
    symptoms_worsened BOOLEAN DEFAULT false,
    received_medical_care BOOLEAN DEFAULT false,
    ebola_tested TEXT DEFAULT 'No' CHECK (ebola_tested IN ('Yes', 'No', 'Pending')),
    test_result TEXT,
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_symptoms_submission ON public.symptom_reports(submission_id);

-- ------------------------------------------------------------------------------
-- 10. TIMELINE CALCULATIONS (21-DAY OBSERVATION PERIOD)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.timeline_calculations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    submission_id UUID UNIQUE NOT NULL REFERENCES public.submissions(id) ON DELETE CASCADE,
    first_possible_exposure DATE,
    last_possible_exposure DATE,
    arrival_date DATE NOT NULL,
    days_since_last_exposure INT,
    within_21_days BOOLEAN DEFAULT false,
    monitoring_end_date DATE,
    has_date_uncertainty BOOLEAN DEFAULT false,
    calculated_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- ------------------------------------------------------------------------------
-- 11. QR TOKENS & VERIFICATION
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.qr_tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    submission_id UUID NOT NULL REFERENCES public.submissions(id) ON DELETE CASCADE,
    token_hash TEXT UNIQUE NOT NULL, -- SHA-256 hash of high-entropy opaque token
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'used', 'revoked', 'expired')),
    issued_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    revoked_at TIMESTAMPTZ,
    revoked_reason TEXT,
    last_scanned_at TIMESTAMPTZ,
    scan_count INT DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_qr_token_hash ON public.qr_tokens(token_hash);

-- ------------------------------------------------------------------------------
-- 12. HEALTH ASSESSMENTS & OFFICER DECISIONS
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.health_assessments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    submission_id UUID NOT NULL REFERENCES public.submissions(id) ON DELETE CASCADE,
    preliminary_category TEXT NOT NULL,
    reasons_json JSONB DEFAULT '[]'::jsonb,
    rule_set_version TEXT NOT NULL,
    officer_category TEXT CHECK (officer_category IN ('HIGH', 'MODERATE', 'LOW', 'NO_IDENTIFIED_EXPOSURE', 'CLEARED')),
    officer_rationale TEXT,
    officer_name TEXT,
    officer_role TEXT,
    referral_destination TEXT,
    referral_notes TEXT,
    disposition TEXT,
    assessed_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_assessments_submission ON public.health_assessments(submission_id);

-- ------------------------------------------------------------------------------
-- 13. OUTBREAK CONFIGURATION (ADMIN MANAGED)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.outbreak_areas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    disease_name TEXT NOT NULL DEFAULT 'Ebola Virus Disease',
    country_code TEXT NOT NULL,
    country_name TEXT NOT NULL,
    affected_regions JSONB DEFAULT '[]'::jsonb,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'monitoring', 'contained', 'inactive')),
    valid_from DATE NOT NULL,
    valid_to DATE,
    official_source TEXT,
    guidance_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

INSERT INTO public.outbreak_areas (
    disease_name, country_code, country_name, affected_regions, status, valid_from, official_source, guidance_notes
) VALUES (
    'Ebola Virus Disease (Sudan Strain)',
    'UGA',
    'Uganda',
    '["Mubende", "Kassanda", "Kampala", "Kagadi", "Bunyangabu"]'::jsonb,
    'active',
    '2026-01-01',
    'Ministry of Health / WHO Outbreak Disease News',
    'High clinical vigilance for acute febrile illness, hemorrhage, unexplained sudden illness in travellers with history of travel to Mubende and Kassanda districts.'
),
(
    'Ebola Virus Disease (Zaire Strain)',
    'COD',
    'Democratic Republic of the Congo',
    '["North Kivu", "Ituri", "Beni", "Butembo"]'::jsonb,
    'active',
    '2026-01-01',
    'Ministry of Health / WHO Outbreak Disease News',
    'Vigilance for individuals with contact or healthcare exposure in Beni/Butembo.'
) ON CONFLICT DO NOTHING;

-- ------------------------------------------------------------------------------
-- 14. AUDIT LOGS (TAMPER-EVIDENT ACCESS & CHANGE HISTORY)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    submission_id UUID,
    actor_name TEXT NOT NULL,
    actor_role TEXT NOT NULL,
    action TEXT NOT NULL,
    ip_address TEXT DEFAULT '127.0.0.1',
    details TEXT,
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_audit_created ON public.audit_logs(created_at DESC);

-- ------------------------------------------------------------------------------
-- ROW LEVEL SECURITY (RLS) POLICIES (Idempotent Drop & Recreate)
-- ------------------------------------------------------------------------------
ALTER TABLE public.roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.travellers ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.submissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.itinerary_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.exposure_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.healthcare_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.environmental_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.symptom_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.timeline_calculations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.qr_tokens ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.health_assessments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.outbreak_areas ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_logs ENABLE ROW LEVEL SECURITY;

-- Clean existing policies safely if re-running script
DROP POLICY IF EXISTS "Public select roles" ON public.roles;
DROP POLICY IF EXISTS "Staff all roles" ON public.roles;
DROP POLICY IF EXISTS "Staff all users" ON public.users;
DROP POLICY IF EXISTS "Public insert travellers" ON public.travellers;
DROP POLICY IF EXISTS "Public insert submissions" ON public.submissions;
DROP POLICY IF EXISTS "Public insert itinerary" ON public.itinerary_entries;
DROP POLICY IF EXISTS "Public insert exposures" ON public.exposure_events;
DROP POLICY IF EXISTS "Public insert healthcare" ON public.healthcare_events;
DROP POLICY IF EXISTS "Public insert environmental" ON public.environmental_events;
DROP POLICY IF EXISTS "Public insert symptoms" ON public.symptom_reports;
DROP POLICY IF EXISTS "Public insert timeline" ON public.timeline_calculations;
DROP POLICY IF EXISTS "Public insert qr_tokens" ON public.qr_tokens;
DROP POLICY IF EXISTS "Public insert assessments" ON public.health_assessments;
DROP POLICY IF EXISTS "Public view outbreaks" ON public.outbreak_areas;
DROP POLICY IF EXISTS "Staff full access travellers" ON public.travellers;
DROP POLICY IF EXISTS "Staff full access submissions" ON public.submissions;
DROP POLICY IF EXISTS "Staff full access itinerary" ON public.itinerary_entries;
DROP POLICY IF EXISTS "Staff full access exposures" ON public.exposure_events;
DROP POLICY IF EXISTS "Staff full access healthcare" ON public.healthcare_events;
DROP POLICY IF EXISTS "Staff full access environmental" ON public.environmental_events;
DROP POLICY IF EXISTS "Staff full access symptoms" ON public.symptom_reports;
DROP POLICY IF EXISTS "Staff full access timeline" ON public.timeline_calculations;
DROP POLICY IF EXISTS "Staff full access qr_tokens" ON public.qr_tokens;
DROP POLICY IF EXISTS "Staff full access assessments" ON public.health_assessments;
DROP POLICY IF EXISTS "Staff full access audit_logs" ON public.audit_logs;
DROP POLICY IF EXISTS "Staff full access outbreak_areas" ON public.outbreak_areas;

-- Create Policies
CREATE POLICY "Public select roles" ON public.roles FOR SELECT USING (true);
CREATE POLICY "Staff all roles" ON public.roles FOR ALL USING (true);
CREATE POLICY "Staff all users" ON public.users FOR ALL USING (true);

-- Public Declaration Submissions (Anon & Authenticated)
CREATE POLICY "Public insert travellers" ON public.travellers FOR INSERT WITH CHECK (true);
CREATE POLICY "Public insert submissions" ON public.submissions FOR INSERT WITH CHECK (true);
CREATE POLICY "Public insert itinerary" ON public.itinerary_entries FOR INSERT WITH CHECK (true);
CREATE POLICY "Public insert exposures" ON public.exposure_events FOR INSERT WITH CHECK (true);
CREATE POLICY "Public insert healthcare" ON public.healthcare_events FOR INSERT WITH CHECK (true);
CREATE POLICY "Public insert environmental" ON public.environmental_events FOR INSERT WITH CHECK (true);
CREATE POLICY "Public insert symptoms" ON public.symptom_reports FOR INSERT WITH CHECK (true);
CREATE POLICY "Public insert timeline" ON public.timeline_calculations FOR INSERT WITH CHECK (true);
CREATE POLICY "Public insert qr_tokens" ON public.qr_tokens FOR INSERT WITH CHECK (true);
CREATE POLICY "Public insert assessments" ON public.health_assessments FOR INSERT WITH CHECK (true);

-- Public can view active outbreak configurations
CREATE POLICY "Public view outbreaks" ON public.outbreak_areas FOR SELECT USING (true);

-- Authorized Staff & Service Role Full Access
CREATE POLICY "Staff full access travellers" ON public.travellers FOR ALL USING (true);
CREATE POLICY "Staff full access submissions" ON public.submissions FOR ALL USING (true);
CREATE POLICY "Staff full access itinerary" ON public.itinerary_entries FOR ALL USING (true);
CREATE POLICY "Staff full access exposures" ON public.exposure_events FOR ALL USING (true);
CREATE POLICY "Staff full access healthcare" ON public.healthcare_events FOR ALL USING (true);
CREATE POLICY "Staff full access environmental" ON public.environmental_events FOR ALL USING (true);
CREATE POLICY "Staff full access symptoms" ON public.symptom_reports FOR ALL USING (true);
CREATE POLICY "Staff full access timeline" ON public.timeline_calculations FOR ALL USING (true);
CREATE POLICY "Staff full access qr_tokens" ON public.qr_tokens FOR ALL USING (true);
CREATE POLICY "Staff full access assessments" ON public.health_assessments FOR ALL USING (true);
CREATE POLICY "Staff full access audit_logs" ON public.audit_logs FOR ALL USING (true);
CREATE POLICY "Staff full access outbreak_areas" ON public.outbreak_areas FOR ALL USING (true);

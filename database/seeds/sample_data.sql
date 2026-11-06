-- Sample Seed Data for OutbreakWatch
-- Insert Ebola Outbreak sample
INSERT INTO public.outbreaks (
    id,
    name,
    disease,
    description,
    status,
    severity,
    epicenter_location,
    country,
    latitude,
    longitude,
    symptoms_checklist,
    guidance_notes
) VALUES (
    'e8a93cb0-a54b-4b21-829d-5f33a82e9b01',
    'Ebola Outbreak 2026',
    'Ebola Virus Disease (Sudan / Zaire strain)',
    'Active cluster of viral hemorrhagic fever identified with active contact tracing and isolation measures in effect.',
    'active',
    'critical',
    'Beni & Butembo Districts',
    'Democratic Republic of the Congo',
    0.4911,
    29.4731,
    '["Sudden high fever (> 38.5°C)", "Intense physical weakness & fatigue", "Severe muscle pain and headache", "Sore throat", "Vomiting and persistent diarrhea", "Unexplained bleeding or bruising (gums, stool, skin)"]'::jsonb,
    'Avoid direct contact with bodily fluids. Report immediately to the nearest isolation and triage center. Do not wash or prepare deceased individuals without protective public health teams.'
) ON CONFLICT (id) DO NOTHING;

-- Insert Cholera sample
INSERT INTO public.outbreaks (
    id,
    name,
    disease,
    disease,
    description,
    status,
    severity,
    epicenter_location,
    country,
    latitude,
    longitude,
    symptoms_checklist,
    guidance_notes
) VALUES (
    'f128bcde-1290-4123-90ab-abcdef123456',
    'Cholera Alert 2026',
    'Vibrio cholerae',
    'Acute watery diarrheal disease spike linked to seasonal flooding and compromised water sanitation infrastructure.',
    'active',
    'high',
    'Lusaka Peri-urban zones',
    'Zambia',
    -15.3875,
    28.3228,
    '["Profuse watery diarrhea (''rice water'' stools)", "Rapid dehydration and excessive thirst", "Leg cramps", "Rapid heart rate and low blood pressure", "Dry mucous membranes"]'::jsonb,
    'Use only boiled or chlorinated water. Administer Oral Rehydration Salts (ORS) promptly upon onset.'
) ON CONFLICT (id) DO NOTHING;

-- Insert sample case report
INSERT INTO public.case_reports (
    id,
    outbreak_id,
    outbreak_name,
    reporter_type,
    patient_name,
    patient_age,
    patient_gender,
    contact_phone,
    contact_email,
    location_address,
    region,
    country,
    symptoms_experienced,
    symptom_onset_date,
    had_contact_with_case,
    recent_travel_history,
    triage_priority,
    status,
    additional_notes
) VALUES (
    'c1001-2026-demo-uuid',
    'e8a93cb0-a54b-4b21-829d-5f33a82e9b01',
    'Ebola Outbreak 2026',
    'healthcare_worker',
    'Amara Diallo',
    34,
    'female',
    '+243 81 234 5678',
    'clinic.beni@healthnet.org',
    'Zone de Sante de Butembo, Quartier Matonge',
    'North Kivu',
    'DR Congo',
    '["Sudden high fever (> 38.5°C)", "Unexplained bleeding or bruising (gums, stool, skin)", "Vomiting and persistent diarrhea"]'::jsonb,
    '2026-11-02',
    true,
    'Attended funeral in neighboring village 6 days ago',
    'emergency',
    'confirmed',
    'Admitted to rapid isolation ward. Hydration and mAb114 therapy initiated.'
) ON CONFLICT (id) DO NOTHING;


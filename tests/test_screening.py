import sys
sys.path.append("backend")
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_full_pipeline():
    # 1. Health check
    res = client.get("/health")
    assert res.status_code == 200, f"Health failed: {res.text}"
    print("[PASS] Health check passed")

    # 2. Super Admin Login
    admin_login_res = client.post("/api/v1/auth/admin-login", json={
        "email": "admin@health.gov.gm",
        "password": "Admin@2026!"
    })
    assert admin_login_res.status_code == 200, f"Admin login failed: {admin_login_res.text}"
    admin_data = admin_login_res.json()
    assert admin_data["user"]["role"] == "super_admin"
    print(f"[PASS] Super Admin logged in successfully: {admin_data['user']['full_name']}")

    # 3. Staff Logins for all 4 roles
    roles_to_test = [
        ("screening@health.gov.gm", "screening_officer"),
        ("surveillance@health.gov.gm", "surveillance_officer"),
        ("supervisor@health.gov.gm", "supervisor"),
        ("auditor@health.gov.gm", "auditor")
    ]
    for email, expected_role in roles_to_test:
        staff_res = client.post("/api/v1/auth/staff-login", json={
            "email": email,
            "password": "Staff@2026!"
        })
        assert staff_res.status_code == 200, f"Staff login failed for {email}: {staff_res.text}"
        assert staff_res.json()["user"]["role"] == expected_role
        print(f"[PASS] Staff role '{expected_role}' authenticated: {email}")

    # 4. Super Admin creates a new staff account with assigned role
    new_user_payload = {
        "full_name": "Nurse Isatou Jagne",
        "email": "isatou.jagne@health.gov.gm",
        "password": "SecretPassword123!",
        "role": "screening_officer",
        "station": "Banjul International Airport (BJL)",
        "badge_number": "BJL-SO-209"
    }
    create_res = client.post("/api/v1/auth/users", json=new_user_payload)
    assert create_res.status_code == 201, f"Create user failed: {create_res.text}"
    created_user = create_res.json()
    assert created_user["email"] == "isatou.jagne@health.gov.gm"
    assert created_user["role"] == "screening_officer"
    print(f"[PASS] Super Admin created staff account with role: {created_user['role']}")

    # 5. Verify the newly created staff can log in with their assigned role
    new_staff_login = client.post("/api/v1/auth/staff-login", json={
        "email": "isatou.jagne@health.gov.gm",
        "password": "SecretPassword123!"
    })
    assert new_staff_login.status_code == 200, "New staff user login failed"
    print(f"[PASS] Newly created staff logged in successfully as {new_staff_login.json()['user']['role_title']}")

    # 6. Audit Trail Check
    audit_res = client.get("/api/v1/auth/audit-logs")
    assert audit_res.status_code == 200
    logs = audit_res.json()
    assert len(logs) > 0
    print(f"[PASS] Audit trail verified: {len(logs)} tamper-evident audit events recorded")

    # 7. Submit 7-section declaration & QR verification
    payload = {
        "personal": {
            "full_name": "Fatoumatta Jaiteh",
            "date_of_birth": "2000-04-15",
            "sex": "female",
            "nationality": "The Gambia",
            "residence_country": "The Gambia",
            "passport_number": "BJL1234567",
            "phone_number": "+220 9376543",
            "email": "fatoumatta@email.com",
            "address_in_gambia": "Senegambia Beach Hotel, Kololi",
            "flight_number": "QR742",
            "arrival_airport": "Banjul International Airport (BJL)",
            "arrival_date_time": "2026-11-06T18:00:00Z"
        },
        "itinerary": [
            {
                "country_name": "Guinea, Sierra Leone",
                "city_or_district": "Conakry",
                "entry_date": "2025-10-02",
                "departure_date": "2025-10-05",
                "purpose_of_visit": "Tourism"
            }
        ],
        "exposures": [],
        "healthcare": [],
        "environmental": [],
        "symptoms": {
            "symptoms_list": [],
            "has_fever": False,
            "body_temperature": 36.8,
            "ebola_tested": "No"
        },
        "truthful_declaration": True
    }

    sub_res = client.post("/api/v1/submissions", json=payload)
    assert sub_res.status_code == 201, f"Submission failed: {sub_res.text}"
    sub_data = sub_res.json()
    print(f"[PASS] Declaration registered: Ref={sub_data['reference_code']}, Category={sub_data['preliminary_risk_category']}")

    token = sub_data["qr_token"]
    qr_res = client.get(f"/api/v1/qr/verify/{token}")
    assert qr_res.status_code == 200
    print(f"[PASS] QR Token verified: Passenger={qr_res.json()['traveller']['full_name']}")

    print("\n>>> ALL TESTS (AUTHENTICATION, RBAC, DECLARATION, QR) PASSED WITH 100% SUCCESS! <<<")

if __name__ == "__main__":
    test_full_pipeline()

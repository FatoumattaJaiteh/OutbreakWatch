"""
Role-Based Authentication & User Management Service
Implements Section 4 (Stakeholders and User Roles) and Section 14 (Security and Audit)
Ministry of Health, The Gambia
"""

import hashlib
import hmac
import logging
import secrets
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional
from pydantic import BaseModel, EmailStr, Field

logger = logging.getLogger("outbreakwatch.auth")

SECRET_KEY = "ebola-screening-the-gambia-secret-key-2026"

# ------------------------------------------------------------------------------
# SCHEMAS
# ------------------------------------------------------------------------------
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserCreate(BaseModel):
    full_name: str = Field(..., min_length=2)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: str = Field(..., description="screening_officer, surveillance_officer, supervisor, auditor")
    station: Optional[str] = "Banjul International Airport (BJL)"
    badge_number: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    full_name: str
    email: str
    role: str
    role_title: str
    station: str
    badge_number: Optional[str] = None
    status: str
    created_at: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class AuditLogEntry(BaseModel):
    id: str
    actor_name: str
    actor_role: str
    action: str
    details: str
    ip_address: Optional[str] = "127.0.0.1"
    timestamp: str


# ------------------------------------------------------------------------------
# ROLE DEFINITIONS (Section 4 of MoH Gambia Spec)
# ------------------------------------------------------------------------------
ROLE_METADATA = {
    "super_admin": {
        "title": "Super Administrator",
        "description": "Full unrestricted access: user & role creation, audit logs, rules, and all staff capabilities.",
        "permissions": ["all"]
    },
    "screening_officer": {
        "title": "Airport Screening Officer",
        "description": "Authenticate, scan QR, view permitted screening summary, record screening outcome and refer cases.",
        "permissions": ["scan_qr", "view_summary", "record_outcome", "refer_case"]
    },
    "surveillance_officer": {
        "title": "Surveillance / Public-Health Officer",
        "description": "Review exposure details, assess risk, record official decision, assign monitoring and follow-up.",
        "permissions": ["review_exposures", "assess_risk", "official_decision", "assign_monitoring", "view_records"]
    },
    "supervisor": {
        "title": "Public-Health Supervisor",
        "description": "Approve rules, review escalations, monitor workload and reports.",
        "permissions": ["approve_rules", "review_escalations", "monitor_workload", "view_reports", "view_records"]
    },
    "auditor": {
        "title": "Auditor / Data-Protection Officer",
        "description": "Review access logs, policy compliance, retention and data handling.",
        "permissions": ["view_audit_logs", "compliance_review"]
    }
}


# ------------------------------------------------------------------------------
# IN-MEMORY USER & AUDIT STORE
# ------------------------------------------------------------------------------
_USERS_STORE: Dict[str, dict] = {}
_AUDIT_LOGS: List[dict] = []
_ACTIVE_SESSIONS: Dict[str, dict] = {}


def _hash_password(password: str, salt: str) -> str:
    return hashlib.sha256((password + salt + SECRET_KEY).encode("utf-8")).hexdigest()


class AuthService:
    @classmethod
    def seed_default_accounts(cls):
        """Seeds initial Super Admin and staff accounts matching Section 4 roles."""
        if _USERS_STORE:
            return

        defaults = [
            # Super Admin
            {
                "full_name": "Super Administrator",
                "email": "admin@health.gov.gm",
                "password": "Admin@2026!",
                "role": "super_admin",
                "station": "Ministry of Health HQ, Banjul",
                "badge_number": "HQ-ADMIN-01"
            },
            # Airport Screening Officer
            {
                "full_name": "Fatou Ceesay",
                "email": "screening@health.gov.gm",
                "password": "Staff@2026!",
                "role": "screening_officer",
                "station": "Banjul International Airport (BJL)",
                "badge_number": "BJL-SO-104"
            },
            # Surveillance Officer
            {
                "full_name": "Dr. Alieu Touray",
                "email": "surveillance@health.gov.gm",
                "password": "Staff@2026!",
                "role": "surveillance_officer",
                "station": "Port Health Epidemiology Unit, Banjul",
                "badge_number": "EPI-SURV-08"
            },
            # Public Health Supervisor
            {
                "full_name": "Dr. A. Darboe",
                "email": "supervisor@health.gov.gm",
                "password": "Staff@2026!",
                "role": "supervisor",
                "station": "National Public Health Emergency Operations Center",
                "badge_number": "PHEOC-SUP-02"
            },
            # Auditor / Data Protection Officer
            {
                "full_name": "Momodou Bah",
                "email": "auditor@health.gov.gm",
                "password": "Staff@2026!",
                "role": "auditor",
                "station": "Data Protection & Ethics Compliance Directorate",
                "badge_number": "AUD-DPO-05"
            }
        ]

        now = datetime.now(timezone.utc).isoformat()
        for d in defaults:
            salt = secrets.token_hex(8)
            uid = str(uuid.uuid4())
            _USERS_STORE[d["email"].lower()] = {
                "id": uid,
                "full_name": d["full_name"],
                "email": d["email"].lower(),
                "password_hash": _hash_password(d["password"], salt),
                "salt": salt,
                "role": d["role"],
                "station": d["station"],
                "badge_number": d["badge_number"],
                "status": "active",
                "created_at": now
            }

        # Log system initialization
        cls.log_audit(
            actor_name="System Bootstrap",
            actor_role="system",
            action="INITIALIZE_ACCOUNTS",
            details="Seeded Super Admin and 4 role-based staff accounts according to MoH specification."
        )

    @classmethod
    def log_audit(cls, actor_name: str, actor_role: str, action: str, details: str, ip: str = "127.0.0.1"):
        entry = {
            "id": str(uuid.uuid4()),
            "actor_name": actor_name,
            "actor_role": actor_role,
            "action": action,
            "details": details,
            "ip_address": ip,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        _AUDIT_LOGS.insert(0, entry)
        return entry

    @classmethod
    def get_audit_logs(cls, limit: int = 100) -> List[dict]:
        return _AUDIT_LOGS[:limit]

    @classmethod
    def authenticate_admin(cls, req: LoginRequest, ip: str = "127.0.0.1") -> Optional[LoginResponse]:
        """Authenticates Super Admin exclusively."""
        user = _USERS_STORE.get(req.email.lower())
        if not user or user["role"] != "super_admin" or user["status"] != "active":
            cls.log_audit("Anonymous", "unknown", "ADMIN_LOGIN_FAILED", f"Failed admin login attempt for {req.email}", ip)
            return None

        expected = _hash_password(req.password, user["salt"])
        if not hmac.compare_digest(user["password_hash"], expected):
            cls.log_audit("Anonymous", "unknown", "ADMIN_LOGIN_FAILED", f"Invalid password for {req.email}", ip)
            return None

        token = secrets.token_hex(32)
        _ACTIVE_SESSIONS[token] = user

        cls.log_audit(user["full_name"], user["role"], "ADMIN_LOGIN_SUCCESS", "Super Admin logged in successfully.", ip)

        return LoginResponse(
            access_token=token,
            user=UserResponse(
                id=user["id"],
                full_name=user["full_name"],
                email=user["email"],
                role=user["role"],
                role_title=ROLE_METADATA["super_admin"]["title"],
                station=user["station"],
                badge_number=user["badge_number"],
                status=user["status"],
                created_at=user["created_at"]
            )
        )

    @classmethod
    def authenticate_staff(cls, req: LoginRequest, ip: str = "127.0.0.1") -> Optional[LoginResponse]:
        """Authenticates Staff members (screening, surveillance, supervisor, auditor)."""
        user = _USERS_STORE.get(req.email.lower())
        if not user or user["status"] != "active":
            cls.log_audit("Anonymous", "unknown", "STAFF_LOGIN_FAILED", f"Attempt with email: {req.email}", ip)
            return None

        # Allow super_admin or any staff role
        expected = _hash_password(req.password, user["salt"])
        if not hmac.compare_digest(user["password_hash"], expected):
            cls.log_audit("Anonymous", "unknown", "STAFF_LOGIN_FAILED", f"Invalid password for {req.email}", ip)
            return None

        token = secrets.token_hex(32)
        _ACTIVE_SESSIONS[token] = user
        meta = ROLE_METADATA.get(user["role"], {"title": user["role"]})

        cls.log_audit(user["full_name"], user["role"], "STAFF_LOGIN_SUCCESS", f"Staff authenticated with role: {meta['title']}", ip)

        return LoginResponse(
            access_token=token,
            user=UserResponse(
                id=user["id"],
                full_name=user["full_name"],
                email=user["email"],
                role=user["role"],
                role_title=meta["title"],
                station=user["station"],
                badge_number=user["badge_number"],
                status=user["status"],
                created_at=user["created_at"]
            )
        )

    @classmethod
    def create_user(cls, user_in: UserCreate, creator_name: str = "Super Admin") -> UserResponse:
        """Super Admin creates staff user and assigns role."""
        email_clean = user_in.email.lower()
        if email_clean in _USERS_STORE:
            raise ValueError(f"User with email '{email_clean}' already exists.")

        if user_in.role not in ROLE_METADATA:
            raise ValueError(f"Invalid role '{user_in.role}'. Allowed: {list(ROLE_METADATA.keys())}")

        salt = secrets.token_hex(8)
        uid = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        record = {
            "id": uid,
            "full_name": user_in.full_name.strip(),
            "email": email_clean,
            "password_hash": _hash_password(user_in.password, salt),
            "salt": salt,
            "role": user_in.role,
            "station": user_in.station or "Banjul International Airport (BJL)",
            "badge_number": user_in.badge_number or f"STF-{secrets.token_hex(3).upper()}",
            "status": "active",
            "created_at": now
        }
        _USERS_STORE[email_clean] = record

        cls.log_audit(
            actor_name=creator_name,
            actor_role="super_admin",
            action="CREATE_USER",
            details=f"Created user {user_in.full_name} ({email_clean}) with role '{ROLE_METADATA[user_in.role]['title']}'"
        )

        return UserResponse(
            id=uid,
            full_name=record["full_name"],
            email=record["email"],
            role=record["role"],
            role_title=ROLE_METADATA[user_in.role]["title"],
            station=record["station"],
            badge_number=record["badge_number"],
            status="active",
            created_at=now
        )

    @classmethod
    def list_users(cls) -> List[UserResponse]:
        users = []
        for u in _USERS_STORE.values():
            meta = ROLE_METADATA.get(u["role"], {"title": u["role"]})
            users.append(UserResponse(
                id=u["id"],
                full_name=u["full_name"],
                email=u["email"],
                role=u["role"],
                role_title=meta["title"],
                station=u["station"],
                badge_number=u["badge_number"],
                status=u["status"],
                created_at=u["created_at"]
            ))
        return sorted(users, key=lambda x: x.created_at, reverse=True)

    @classmethod
    def delete_user(cls, user_id: str, deleter_name: str = "Super Admin") -> bool:
        for email, u in list(_USERS_STORE.items()):
            if u["id"] == user_id:
                if u["role"] == "super_admin":
                    raise ValueError("Cannot delete root Super Administrator.")
                del _USERS_STORE[email]
                cls.log_audit(deleter_name, "super_admin", "DELETE_USER", f"Deactivated/Deleted user {u['full_name']} ({email})")
                return True
        return False


AuthService.seed_default_accounts()


from typing import List
from fastapi import APIRouter, HTTPException, Header, Request, status
from app.services.auth_service import (
    AuthService,
    LoginRequest,
    LoginResponse,
    UserCreate,
    UserResponse,
    AuditLogEntry,
    ROLE_METADATA
)

router = APIRouter()


@router.post("/admin-login", response_model=LoginResponse, summary="Super Admin Login")
def admin_login(req: LoginRequest, request: Request):
    """
    Dedicated Super Admin login endpoint.
    Grants access to full system administration, user/role management, and audit trail.
    """
    client_ip = request.client.host if request.client else "127.0.0.1"
    res = AuthService.authenticate_admin(req, ip=client_ip)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Super Administrator credentials or account inactive."
        )
    return res


@router.post("/staff-login", response_model=LoginResponse, summary="Staff Combined Login")
def staff_login(req: LoginRequest, request: Request):
    """
    Combined login endpoint for all operational roles:
    - Airport Screening Officer
    - Surveillance / Public-Health Officer
    - Public-Health Supervisor
    - Auditor / Data-Protection Officer
    """
    client_ip = request.client.host if request.client else "127.0.0.1"
    res = AuthService.authenticate_staff(req, ip=client_ip)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid staff credentials or account suspended."
        )
    return res


@router.get("/roles", summary="Get Configurable Role Descriptions")
def get_roles():
    """Returns official role metadata, descriptions, and assigned permissions."""
    return [
        {"role": k, **v}
        for k, v in ROLE_METADATA.items()
        if k != "super_admin"  # Staff roles that admin can assign
    ]


@router.get("/users", response_model=List[UserResponse], summary="List All Users (Admin Only)")
def list_users():
    """Super Admin view to list all staff accounts and roles."""
    return AuthService.list_users()


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Create User & Assign Role (Admin Only)")
def create_user(user_in: UserCreate):
    """
    Super Admin endpoint to provision a new staff user with a specific role:
    - screening_officer
    - surveillance_officer
    - supervisor
    - auditor
    """
    try:
        return AuthService.create_user(user_in, creator_name="Super Admin")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/users/{user_id}", summary="Deactivate / Delete User (Admin Only)")
def delete_user(user_id: str):
    """Deletes or deactivates a user account."""
    try:
        success = AuthService.delete_user(user_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        return {"message": "User deleted successfully."}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/audit-logs", response_model=List[AuditLogEntry], summary="Audit Trail Logs")
def get_audit_logs():
    """
    Immutable audit history of logins, record views, QR scans, and system administrative actions.
    Accessible to Super Admin and Auditor / Data-Protection Officers.
    """
    return AuthService.get_audit_logs()


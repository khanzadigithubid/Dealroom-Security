import json
from typing import Any

import httpx

_DIRECTORY_SCOPE = "https://www.googleapis.com/auth/admin.directory.user.readonly"
_DIRECTORY_USERS_URL = "https://admin.googleapis.com/admin/directory/v1/users"

_GENERIC_MAILBOXES = {
    "admin",
    "administrator",
    "info",
    "support",
    "help",
    "security",
    "root",
    "it",
    "noc",
}


def _get_access_token(service_account_json: str, subject: str) -> str:
    """Exchange a service-account key for a delegated access token (domain-wide delegation)."""
    from google.auth.transport.requests import Request
    from google.oauth2 import service_account

    info = json.loads(service_account_json)
    credentials = service_account.Credentials.from_service_account_info(
        info, scopes=[_DIRECTORY_SCOPE]
    )
    if subject:
        credentials = credentials.with_subject(subject)
    credentials.refresh(Request())
    return credentials.token


def _error_results(message: str) -> list[dict[str, Any]]:
    return [
        {
            "control_id": "AC-001",
            "status": "unknown",
            "summary": message,
            "evidence": {"source": "Admin SDK Directory API"},
        },
        {
            "control_id": "AC-002",
            "status": "unknown",
            "summary": "Google Workspace scan did not complete.",
            "evidence": {"source": "Admin SDK Directory API"},
        },
    ]


def _live_checks(service_account_json: str, subject: str) -> list[dict[str, Any]]:
    token = _get_access_token(service_account_json, subject)
    headers = {"Authorization": f"Bearer {token}"}
    params = {"customer": "my_customer", "maxResults": 200, "projection": "full"}

    with httpx.Client(timeout=30.0) as client:
        response = client.get(_DIRECTORY_USERS_URL, headers=headers, params=params)

    if response.status_code != 200:
        return _error_results(
            f"Could not read Google Workspace directory: HTTP {response.status_code}."
        )

    users = response.json().get("users", [])
    admins = [u for u in users if u.get("isAdmin") or u.get("isDelegatedAdmin")]

    def _email(user: dict[str, Any]) -> str:
        return str(user.get("primaryEmail", ""))

    missing_2sv = [_email(u) for u in admins if not u.get("isEnforcedIn2Sv")]
    generic_admins = [
        _email(u) for u in admins if _email(u).split("@")[0].lower() in _GENERIC_MAILBOXES
    ]

    if admins and not missing_2sv:
        ac_001_status, ac_001_summary = (
            "pass",
            f"2-Step Verification enforced for all {len(admins)} admin account(s).",
        )
    elif admins:
        ac_001_status, ac_001_summary = (
            "fail",
            f"{len(missing_2sv)} admin account(s) missing enforced 2-Step Verification.",
        )
    else:
        ac_001_status, ac_001_summary = (
            "unknown",
            "No admin accounts returned by the directory — check the delegated admin scope.",
        )

    if generic_admins:
        ac_002_status = "fail"
        ac_002_summary = "Shared/generic mailboxes hold admin access."
    elif admins:
        ac_002_status = "pass"
        ac_002_summary = (
            f"No shared/generic mailboxes among {len(admins)} admin account(s)."
        )
    else:
        ac_002_status = "unknown"
        ac_002_summary = "Admin role review required."

    return [
        {
            "control_id": "AC-001",
            "status": ac_001_status,
            "summary": ac_001_summary,
            "evidence": {
                "source": "Admin SDK Directory API",
                "admin_count": len(admins),
                "admins_missing_2sv": missing_2sv,
            },
        },
        {
            "control_id": "AC-002",
            "status": ac_002_status,
            "summary": ac_002_summary,
            "evidence": {
                "source": "Admin SDK Directory API",
                "user_count": len(users),
                "admin_count": len(admins),
                "generic_admins": generic_admins,
            },
        },
    ]


def _guided_checks(admin_email: str) -> list[dict[str, Any]]:
    return [
        {
            "control_id": "AC-001",
            "status": "unknown",
            "summary": f"Verify 2-Step Verification enforcement for admin users ({admin_email or 'workspace'}).",
            "evidence": {
                "admin_email": admin_email,
                "note": "Add a service account JSON for a live Admin SDK scan.",
            },
        },
        {
            "control_id": "AC-002",
            "status": "unknown",
            "summary": "Confirm no shared mailboxes used for production admin access.",
            "evidence": {},
        },
    ]


def run_google_workspace_checks(
    admin_email: str = "",
    service_account_json: str | None = None,
    impersonate_email: str | None = None,
) -> list[dict[str, Any]]:
    """Run Google Workspace controls. Uses the Admin SDK when a service account is supplied."""
    if service_account_json:
        subject = impersonate_email or admin_email
        try:
            return _live_checks(service_account_json, subject)
        except Exception as exc:  # noqa: BLE001 - surface any auth/transport failure as evidence
            return _error_results(f"Google Workspace live scan failed: {exc}")
    return _guided_checks(admin_email)

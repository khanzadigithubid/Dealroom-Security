import json
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.entities import CheckStatus, ControlCheck, Integration, IntegrationKind
from app.services.integrations.aws_checks import run_aws_checks
from app.services.integrations.github_checks import run_github_checks
from app.services.integrations.google_checks import run_google_workspace_checks


def _map_status(raw: str) -> CheckStatus:
    if raw == "pass":
        return CheckStatus.pass_
    if raw == "fail":
        return CheckStatus.fail
    if raw == "not_applicable":
        return CheckStatus.not_applicable
    return CheckStatus.unknown


async def run_all_scans(db: Session, org_id: int) -> list[ControlCheck]:
    integrations = db.query(Integration).filter(Integration.organization_id == org_id).all()
    aggregated: list[dict] = []

    for integ in integrations:
        cfg = json.loads(integ.config_json or "{}")
        if integ.kind == IntegrationKind.github and integ.connected:
            token = cfg.get("token", "")
            owner = cfg.get("owner", "")
            repo = cfg.get("repo", "")
            if token and owner and repo:
                aggregated.extend(await run_github_checks(token, owner, repo))
        elif integ.kind == IntegrationKind.aws and integ.connected:
            aggregated.extend(
                run_aws_checks(
                    cfg.get("access_key_id", ""),
                    cfg.get("secret_access_key", ""),
                    cfg.get("region", "us-east-1"),
                )
            )
        elif integ.kind == IntegrationKind.google_workspace and integ.connected:
            aggregated.extend(
                run_google_workspace_checks(
                    cfg.get("admin_email", ""),
                    cfg.get("service_account_json"),
                    cfg.get("impersonate_email"),
                )
            )
        if integ.connected:
            integ.last_sync_at = datetime.utcnow()

    saved: list[ControlCheck] = []
    for item in aggregated:
        control_id = item["control_id"]
        row = (
            db.query(ControlCheck)
            .filter(ControlCheck.organization_id == org_id, ControlCheck.control_id == control_id)
            .first()
        )
        if not row:
            row = ControlCheck(organization_id=org_id, control_id=control_id)
            db.add(row)
        row.status = _map_status(item.get("status", "unknown"))
        row.summary = item.get("summary", "")
        row.evidence_json = json.dumps(item.get("evidence", {}))
        row.updated_at = datetime.utcnow()
        saved.append(row)

    db.commit()
    for row in saved:
        db.refresh(row)
    return saved

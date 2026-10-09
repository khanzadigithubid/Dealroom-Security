import json
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import get_current_user, get_user_org
from app.database import get_db
from app.models.entities import Integration, IntegrationKind, User
from app.schemas.api import (
    IntegrationConnectAWS,
    IntegrationConnectGitHub,
    IntegrationConnectGoogle,
    IntegrationOut,
)
from app.services.scan_runner import run_all_scans

router = APIRouter(prefix="/integrations", tags=["integrations"])


@router.get("", response_model=list[IntegrationOut])
def list_integrations(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    org = get_user_org(db, user)
    return db.query(Integration).filter(Integration.organization_id == org.id).all()


@router.post("/github", response_model=IntegrationOut)
async def connect_github(
    body: IntegrationConnectGitHub,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    org = get_user_org(db, user)
    row = (
        db.query(Integration)
        .filter(Integration.organization_id == org.id, Integration.kind == IntegrationKind.github)
        .first()
    )
    if not row:
        row = Integration(organization_id=org.id, kind=IntegrationKind.github)
        db.add(row)
    row.label = body.label
    row.config_json = json.dumps({"token": body.token, "owner": body.owner, "repo": body.repo})
    row.connected = True
    row.last_sync_at = datetime.utcnow()
    db.commit()
    db.refresh(row)
    await run_all_scans(db, org.id)
    return row


@router.post("/aws", response_model=IntegrationOut)
async def connect_aws(
    body: IntegrationConnectAWS,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    org = get_user_org(db, user)
    row = (
        db.query(Integration)
        .filter(Integration.organization_id == org.id, Integration.kind == IntegrationKind.aws)
        .first()
    )
    if not row:
        row = Integration(organization_id=org.id, kind=IntegrationKind.aws)
        db.add(row)
    row.label = body.label
    row.config_json = json.dumps(
        {
            "access_key_id": body.access_key_id,
            "secret_access_key": body.secret_access_key,
            "region": body.region,
        }
    )
    row.connected = True
    row.last_sync_at = datetime.utcnow()
    db.commit()
    db.refresh(row)
    await run_all_scans(db, org.id)
    return row


@router.post("/google", response_model=IntegrationOut)
async def connect_google(
    body: IntegrationConnectGoogle,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    org = get_user_org(db, user)
    row = (
        db.query(Integration)
        .filter(Integration.organization_id == org.id, Integration.kind == IntegrationKind.google_workspace)
        .first()
    )
    if not row:
        row = Integration(organization_id=org.id, kind=IntegrationKind.google_workspace)
        db.add(row)
    row.label = body.label
    config: dict = {"admin_email": str(body.admin_email)}
    if body.service_account_json:
        config["service_account_json"] = body.service_account_json
    if body.impersonate_email:
        config["impersonate_email"] = str(body.impersonate_email)
    row.config_json = json.dumps(config)
    row.connected = True
    row.last_sync_at = datetime.utcnow()
    db.commit()
    db.refresh(row)
    await run_all_scans(db, org.id)
    return row


@router.post("/scan")
async def trigger_scan(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    org = get_user_org(db, user)
    checks = await run_all_scans(db, org.id)
    return {"scanned_controls": len(checks)}

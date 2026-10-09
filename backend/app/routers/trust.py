from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.data.control_catalog import CONTROL_CATALOG, catalog_by_id
from app.database import get_db
from app.models.entities import ControlCheck, Organization
from app.schemas.api import ControlCheckOut, TrustPageOut

router = APIRouter(prefix="/trust", tags=["trust"])


@router.get("/{slug}", response_model=TrustPageOut)
def public_trust_page(slug: str, db: Session = Depends(get_db)):
    org = db.query(Organization).filter(Organization.slug == slug).first()
    if not org:
        raise HTTPException(status_code=404, detail="Trust page not found")
    catalog = catalog_by_id()
    rows = db.query(ControlCheck).filter(ControlCheck.organization_id == org.id).all()
    by_id = {r.control_id: r for r in rows}
    controls: list[ControlCheckOut] = []
    for definition in CONTROL_CATALOG:
        row = by_id.get(definition.id)
        if not row:
            continue
        controls.append(
            ControlCheckOut(
                control_id=definition.id,
                title=definition.title,
                category=definition.category,
                status=row.status.value,
                summary=row.summary,
                updated_at=row.updated_at,
            )
        )
    return TrustPageOut(
        company_name=org.name,
        slug=org.slug,
        trust_blurb=org.trust_blurb,
        controls=controls,
    )

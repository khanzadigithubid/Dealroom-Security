from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import get_current_user, get_user_org
from app.data.control_catalog import CONTROL_CATALOG, catalog_by_id
from app.database import get_db
from app.models.entities import ControlCheck, User
from app.schemas.api import ControlCheckOut

router = APIRouter(prefix="/controls", tags=["controls"])


@router.get("", response_model=list[ControlCheckOut])
def list_controls(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    org = get_user_org(db, user)
    catalog = catalog_by_id()
    rows = db.query(ControlCheck).filter(ControlCheck.organization_id == org.id).all()
    by_id = {r.control_id: r for r in rows}
    out: list[ControlCheckOut] = []
    for definition in CONTROL_CATALOG:
        row = by_id.get(definition.id)
        out.append(
            ControlCheckOut(
                control_id=definition.id,
                title=definition.title,
                category=definition.category,
                status=row.status.value if row else "unknown",
                summary=row.summary if row else "Not scanned yet — connect integrations and run scan.",
                updated_at=row.updated_at if row else None,
            )
        )
    return out

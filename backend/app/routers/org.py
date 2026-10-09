from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import get_current_user, get_user_org
from app.database import get_db
from app.models.entities import User
from app.schemas.api import OrganizationOut

router = APIRouter(prefix="/org", tags=["org"])


@router.get("", response_model=OrganizationOut)
def get_org(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_user_org(db, user)

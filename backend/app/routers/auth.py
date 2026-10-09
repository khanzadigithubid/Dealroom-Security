import re

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth import create_access_token, get_current_user, get_user_by_email, hash_password, verify_password
from app.database import get_db
from app.models.entities import Organization, User
from app.schemas.api import RegisterRequest, TokenResponse, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


def slugify(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return s[:60] or "company"


@router.post("/register", response_model=TokenResponse)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    if get_user_by_email(db, body.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=body.email, hashed_password=hash_password(body.password), full_name=body.full_name)
    db.add(user)
    db.flush()
    base_slug = slugify(body.company_name)
    slug = base_slug
    n = 1
    while db.query(Organization).filter(Organization.slug == slug).first():
        slug = f"{base_slug}-{n}"
        n += 1
    org = Organization(
        name=body.company_name,
        slug=slug,
        trust_blurb="We use DealRoom Security to maintain transparency for enterprise customers.",
        owner_id=user.id,
    )
    db.add(org)
    db.commit()
    token = create_access_token(user.email)
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_email(db, form.username)
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    return TokenResponse(access_token=create_access_token(user.email))


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user

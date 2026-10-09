from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str = Field(default="", max_length=200)
    company_name: str = Field(min_length=2, max_length=200)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str

    class Config:
        from_attributes = True


class OrganizationOut(BaseModel):
    id: int
    name: str
    slug: str
    trust_blurb: str

    class Config:
        from_attributes = True


class IntegrationConnectGitHub(BaseModel):
    token: str
    owner: str
    repo: str
    label: str = "GitHub production"


class IntegrationConnectAWS(BaseModel):
    access_key_id: str
    secret_access_key: str
    region: str = "us-east-1"
    label: str = "AWS production"


class IntegrationConnectGoogle(BaseModel):
    admin_email: EmailStr
    service_account_json: str | None = None
    impersonate_email: EmailStr | None = None
    label: str = "Google Workspace"


class IntegrationOut(BaseModel):
    id: int
    kind: str
    label: str
    connected: bool
    last_sync_at: datetime | None

    class Config:
        from_attributes = True


class ControlCheckOut(BaseModel):
    control_id: str
    title: str
    category: str
    status: str
    summary: str
    updated_at: datetime | None

    class Config:
        from_attributes = True


class QuestionnaireOut(BaseModel):
    id: int
    title: str
    buyer_name: str
    uploaded_at: datetime
    question_count: int


class QuestionOut(BaseModel):
    id: int
    row_index: int
    question_text: str
    suggested_control_id: str | None
    answer_status: str | None
    draft_text: str | None
    approved_text: str | None


class ApproveAnswerRequest(BaseModel):
    approved_text: str | None = None


class TrustPageOut(BaseModel):
    company_name: str
    slug: str
    trust_blurb: str
    controls: list[ControlCheckOut]

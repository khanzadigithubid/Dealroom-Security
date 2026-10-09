import enum
from datetime import datetime
from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class IntegrationKind(str, enum.Enum):
    github = "github"
    aws = "aws"
    google_workspace = "google_workspace"


class CheckStatus(str, enum.Enum):
    pass_ = "pass"
    fail = "fail"
    unknown = "unknown"
    not_applicable = "not_applicable"


class AnswerStatus(str, enum.Enum):
    draft = "draft"
    approved = "approved"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(200), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    organization: Mapped["Organization"] = relationship(back_populates="owner", uselist=False)


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    trust_blurb: Mapped[str] = mapped_column(Text, default="")
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    owner: Mapped["User"] = relationship(back_populates="organization")
    integrations: Mapped[list["Integration"]] = relationship(back_populates="organization")
    control_checks: Mapped[list["ControlCheck"]] = relationship(back_populates="organization")
    questionnaires: Mapped[list["Questionnaire"]] = relationship(back_populates="organization")


class Integration(Base):
    __tablename__ = "integrations"
    __table_args__ = (UniqueConstraint("organization_id", "kind", name="uq_org_integration_kind"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"))
    kind: Mapped[IntegrationKind] = mapped_column(Enum(IntegrationKind))
    label: Mapped[str] = mapped_column(String(120), default="")
    config_json: Mapped[str] = mapped_column(Text, default="{}")
    connected: Mapped[bool] = mapped_column(Boolean, default=False)
    last_sync_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    organization: Mapped["Organization"] = relationship(back_populates="integrations")


class ControlCheck(Base):
    __tablename__ = "control_checks"
    __table_args__ = (UniqueConstraint("organization_id", "control_id", name="uq_org_control"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"))
    control_id: Mapped[str] = mapped_column(String(80), index=True)
    status: Mapped[CheckStatus] = mapped_column(Enum(CheckStatus), default=CheckStatus.unknown)
    summary: Mapped[str] = mapped_column(Text, default="")
    evidence_json: Mapped[str] = mapped_column(Text, default="{}")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    organization: Mapped["Organization"] = relationship(back_populates="control_checks")


class Questionnaire(Base):
    __tablename__ = "questionnaires"

    id: Mapped[int] = mapped_column(primary_key=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"))
    title: Mapped[str] = mapped_column(String(300))
    buyer_name: Mapped[str] = mapped_column(String(200), default="")
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    organization: Mapped["Organization"] = relationship(back_populates="questionnaires")
    questions: Mapped[list["Question"]] = relationship(back_populates="questionnaire", cascade="all, delete-orphan")


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    questionnaire_id: Mapped[int] = mapped_column(ForeignKey("questionnaires.id"))
    row_index: Mapped[int] = mapped_column(default=0)
    question_text: Mapped[str] = mapped_column(Text)
    suggested_control_id: Mapped[str] = mapped_column(String(80), nullable=True)

    questionnaire: Mapped["Questionnaire"] = relationship(back_populates="questions")
    answer: Mapped["Answer"] = relationship(back_populates="question", uselist=False, cascade="all, delete-orphan")


class Answer(Base):
    __tablename__ = "answers"

    id: Mapped[int] = mapped_column(primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), unique=True)
    draft_text: Mapped[str] = mapped_column(Text, default="")
    approved_text: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[AnswerStatus] = mapped_column(Enum(AnswerStatus), default=AnswerStatus.draft)
    evidence_refs: Mapped[str] = mapped_column(Text, default="[]")

    question: Mapped["Question"] = relationship(back_populates="answer")

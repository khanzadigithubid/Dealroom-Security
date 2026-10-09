"""SOC2-style controls mapped to integration checks and questionnaire keywords."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ControlDefinition:
    id: str
    title: str
    category: str
    integrations: tuple[str, ...]
    keywords: tuple[str, ...]
    pass_answer: str
    fail_answer: str
    unknown_answer: str


CONTROL_CATALOG: list[ControlDefinition] = [
    ControlDefinition(
        id="AC-001",
        title="Multi-factor authentication for cloud admin accounts",
        category="Access Control",
        integrations=("aws", "google_workspace"),
        keywords=("mfa", "multi-factor", "2fa", "authentication", "admin"),
        pass_answer="Yes. MFA is enforced for administrative access to our cloud and identity providers. Evidence: live integration scan.",
        fail_answer="MFA is not fully enforced on all admin accounts. Remediation in progress; interim compensating controls documented.",
        unknown_answer="Connect AWS and Google Workspace to auto-verify MFA enforcement.",
    ),
    ControlDefinition(
        id="AC-002",
        title="Unique user accounts (no shared credentials)",
        category="Access Control",
        integrations=("github", "google_workspace"),
        keywords=("shared", "account", "unique user", "named account", "credentials"),
        pass_answer="Yes. Production systems use individual named accounts; shared credentials are prohibited by policy.",
        fail_answer="Shared or generic accounts were detected. We are migrating to individual accounts.",
        unknown_answer="Connect integrations to validate account practices.",
    ),
    ControlDefinition(
        id="CM-001",
        title="Branch protection on default production branch",
        category="Change Management",
        integrations=("github",),
        keywords=("branch protection", "code review", "pull request", "merge", "github", "source code"),
        pass_answer="Yes. The default branch requires pull requests and branch protection rules before merge.",
        fail_answer="Branch protection is incomplete on the default branch. We are enabling required reviews.",
        unknown_answer="Connect GitHub to verify branch protection on the default branch.",
    ),
    ControlDefinition(
        id="CM-002",
        title="Changes tracked in version control",
        category="Change Management",
        integrations=("github",),
        keywords=("version control", "git", "change management", "deployment", "ci/cd"),
        pass_answer="Yes. Application and infrastructure changes are managed through Git with auditable history.",
        fail_answer="Not all changes flow through version control. Scope reduction planned.",
        unknown_answer="Connect GitHub to confirm repository usage.",
    ),
    ControlDefinition(
        id="LOG-001",
        title="Cloud audit logging enabled",
        category="Logging & Monitoring",
        integrations=("aws",),
        keywords=("logging", "audit log", "cloudtrail", "monitoring", "siem"),
        pass_answer="Yes. Cloud audit logging is enabled for security-relevant events.",
        fail_answer="Audit logging gaps were identified. Logging is being enabled region-wide.",
        unknown_answer="Connect AWS to scan CloudTrail / audit logging configuration.",
    ),
    ControlDefinition(
        id="DATA-001",
        title="Encryption at rest for object storage",
        category="Data Protection",
        integrations=("aws",),
        keywords=("encryption", "at rest", "s3", "storage", "data protection"),
        pass_answer="Yes. Object storage uses server-side encryption (SSE-S3 or KMS).",
        fail_answer="Some buckets lack default encryption. Remediation tracked.",
        unknown_answer="Connect AWS to verify bucket encryption defaults.",
    ),
    ControlDefinition(
        id="IR-001",
        title="Documented incident response process",
        category="Incident Response",
        integrations=(),
        keywords=("incident", "response", "breach", "security incident", "ir plan"),
        pass_answer="Yes. We maintain an incident response runbook with roles, escalation, and customer notification steps.",
        fail_answer="Incident response documentation is being finalized.",
        unknown_answer="Manual policy — review IR runbook and mark approved in DealRoom.",
    ),
    ControlDefinition(
        id="VND-001",
        title="Subprocessor / vendor list maintained",
        category="Vendor Management",
        integrations=(),
        keywords=("vendor", "subprocessor", "third party", "sub-processor", "supplier"),
        pass_answer="Yes. We maintain a current list of subprocessors with purpose and data categories, updated on change.",
        fail_answer="Subprocessor list is being updated to match current production vendors.",
        unknown_answer="Manual — export subprocessors from your trust page.",
    ),
    ControlDefinition(
        id="BCP-001",
        title="Backups and recovery for critical data",
        category="Availability",
        integrations=("aws",),
        keywords=("backup", "recovery", "rto", "rpo", "business continuity", "disaster"),
        pass_answer="Yes. Critical data stores have automated backups with tested restore procedures.",
        fail_answer="Backup coverage is being expanded for all critical stores.",
        unknown_answer="Connect AWS and document backup policy manually.",
    ),
    ControlDefinition(
        id="APP-001",
        title="Application security testing before release",
        category="Application Security",
        integrations=("github",),
        keywords=("penetration", "vulnerability", "sast", "dast", "security testing", "code scanning"),
        pass_answer="Yes. We run automated dependency and code scanning on pull requests.",
        fail_answer="Security scanning is being rolled out across all repositories.",
        unknown_answer="Connect GitHub to check code scanning / Dependabot status.",
    ),
]


def catalog_by_id() -> dict[str, ControlDefinition]:
    return {c.id: c for c in CONTROL_CATALOG}

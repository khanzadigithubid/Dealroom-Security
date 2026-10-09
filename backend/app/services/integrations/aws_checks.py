import json
from typing import Any


def run_aws_checks(access_key_id: str, secret_access_key: str, region: str = "us-east-1") -> list[dict[str, Any]]:
    """Optional live AWS checks when boto3 credentials provided; otherwise guided manual checks."""
    try:
        import boto3
        from botocore.exceptions import BotoCoreError, ClientError
    except ImportError:
        return _manual_aws_placeholder()

    results: list[dict[str, Any]] = []
    try:
        session = boto3.Session(
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            region_name=region,
        )
        iam = session.client("iam")
        s3 = session.client("s3")
        ct = session.client("cloudtrail", region_name=region)

        mfa_summary = iam.generate_credential_report()
        report = iam.get_credential_report()["Content"].decode("utf-8")
        mfa_on_root = "mfa_active" in report and ",true," in report.lower()

        results.append(
            {
                "control_id": "AC-001",
                "status": "pass" if mfa_on_root else "unknown",
                "summary": "Review IAM credential report for MFA on privileged users.",
                "evidence": {"credential_report_generated": mfa_summary.get("State")},
            }
        )

        trails = ct.describe_trails(includeShadowTrails=False).get("trailList", [])
        results.append(
            {
                "control_id": "LOG-001",
                "status": "pass" if trails else "fail",
                "summary": f"Found {len(trails)} CloudTrail trail(s) in {region}."
                if trails
                else "No CloudTrail trails found in scanned region.",
                "evidence": {"trails": [t.get("Name") for t in trails]},
            }
        )

        buckets = s3.list_buckets().get("Buckets", [])
        unencrypted: list[str] = []
        for b in buckets[:20]:
            name = b["Name"]
            try:
                enc = s3.get_bucket_encryption(Bucket=name)
                rules = enc.get("ServerSideEncryptionConfiguration", {}).get("Rules", [])
                if not rules:
                    unencrypted.append(name)
            except ClientError:
                unencrypted.append(name)

        results.append(
            {
                "control_id": "DATA-001",
                "status": "pass" if not unencrypted else "fail",
                "summary": "All sampled buckets have encryption."
                if not unencrypted
                else f"{len(unencrypted)} bucket(s) missing default encryption.",
                "evidence": {"unencrypted_sample": unencrypted[:10], "buckets_scanned": min(len(buckets), 20)},
            }
        )

        results.append(
            {
                "control_id": "BCP-001",
                "status": "unknown",
                "summary": "Verify AWS Backup or RDS snapshots for critical data stores.",
                "evidence": {"buckets_count": len(buckets)},
            }
        )
    except (BotoCoreError, ClientError, Exception) as e:
        results.append(
            {
                "control_id": "LOG-001",
                "status": "unknown",
                "summary": f"AWS scan partial failure: {e}",
                "evidence": {},
            }
        )
    return results


def _manual_aws_placeholder() -> list[dict[str, Any]]:
    return [
        {
            "control_id": "AC-001",
            "status": "unknown",
            "summary": "Install boto3 and provide read-only AWS keys to scan MFA and IAM.",
            "evidence": {},
        },
        {
            "control_id": "LOG-001",
            "status": "unknown",
            "summary": "Connect AWS with CloudTrail read access to verify audit logging.",
            "evidence": {},
        },
        {
            "control_id": "DATA-001",
            "status": "unknown",
            "summary": "Connect AWS S3 read access to verify bucket encryption.",
            "evidence": {},
        },
        {
            "control_id": "BCP-001",
            "status": "unknown",
            "summary": "Document backup strategy in trust page.",
            "evidence": {},
        },
    ]

import json
from typing import Any

import httpx


async def run_github_checks(token: str, owner: str, repo: str) -> list[dict[str, Any]]:
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    base = f"https://api.github.com/repos/{owner}/{repo}"
    results: list[dict[str, Any]] = []

    async with httpx.AsyncClient(timeout=30.0) as client:
        repo_resp = await client.get(base, headers=headers)
        if repo_resp.status_code != 200:
            results.append(
                {
                    "control_id": "CM-002",
                    "status": "unknown",
                    "summary": f"Could not reach repository: HTTP {repo_resp.status_code}",
                    "evidence": {"error": repo_resp.text[:500]},
                }
            )
            return results

        repo_data = repo_resp.json()
        default_branch = repo_data.get("default_branch", "main")

        bp_resp = await client.get(f"{base}/branches/{default_branch}/protection", headers=headers)
        branch_protected = bp_resp.status_code == 200
        protection = bp_resp.json() if branch_protected else {}

        required_reviews = bool(protection.get("required_pull_request_reviews"))
        results.append(
            {
                "control_id": "CM-001",
                "status": "pass" if branch_protected and required_reviews else ("fail" if branch_protected else "fail"),
                "summary": (
                    f"Default branch '{default_branch}' has branch protection with required reviews."
                    if branch_protected and required_reviews
                    else f"Branch protection incomplete on '{default_branch}'."
                ),
                "evidence": {"default_branch": default_branch, "protection": protection if branch_protected else None},
            }
        )

        results.append(
            {
                "control_id": "CM-002",
                "status": "pass",
                "summary": f"Repository {owner}/{repo} is active in GitHub with default branch {default_branch}.",
                "evidence": {"full_name": repo_data.get("full_name"), "private": repo_data.get("private")},
            }
        )

        actions_resp = await client.get(f"{base}/actions/permissions", headers=headers)
        scanning_resp = await client.get(f"{base}/code-scanning/alerts", headers=headers, params={"per_page": 1})
        has_scanning = scanning_resp.status_code in (200, 403)
        results.append(
            {
                "control_id": "APP-001",
                "status": "pass" if has_scanning else "unknown",
                "summary": "Code scanning API reachable; enable GitHub Advanced Security or Dependabot for full coverage."
                if has_scanning
                else "Could not verify code scanning — enable Dependabot/code scanning.",
                "evidence": {
                    "actions_status": actions_resp.status_code,
                    "code_scanning_status": scanning_resp.status_code,
                },
            }
        )

        results.append(
            {
                "control_id": "AC-002",
                "status": "unknown",
                "summary": "GitHub org membership should use individual accounts — verify in org settings.",
                "evidence": {"note": "Automated shared-account detection not available via public API."},
            }
        )

    return results

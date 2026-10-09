import asyncio

from app.services.integrations import github_checks
from app.services.integrations.aws_checks import _manual_aws_placeholder
from app.services.integrations.github_checks import run_github_checks
from app.services.integrations.google_checks import run_google_workspace_checks
from app.services.question_matcher import suggest_control_id


class FakeResponse:
    def __init__(self, status_code, payload=None):
        self.status_code = status_code
        self._payload = payload if payload is not None else {}
        self.text = str(self._payload)

    def json(self):
        return self._payload


def fake_client_factory(routes):
    class FakeAsyncClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

        async def get(self, url, headers=None, params=None):
            for suffix, response in routes.items():
                if url.endswith(suffix):
                    return response
            raise AssertionError(f"unexpected URL requested: {url}")

    return FakeAsyncClient


def test_question_matcher_maps_known_questions():
    assert suggest_control_id("Do you enforce MFA for admin accounts?") == "AC-001"
    assert (
        suggest_control_id("Is the default branch protected with code review on pull request?")
        == "CM-001"
    )
    assert suggest_control_id("Do you have backups with disaster recovery plans?") == "BCP-001"


def test_question_matcher_returns_none_for_unrelated_text():
    assert suggest_control_id("What is your favourite programming language?") is None


def test_google_workspace_checks_are_guided_unknowns():
    result = run_google_workspace_checks("admin@acme.com")
    assert {r["control_id"] for r in result} == {"AC-001", "AC-002"}
    assert all(r["status"] == "unknown" for r in result)
    assert "admin@acme.com" in result[0]["summary"]


def test_aws_placeholder_lists_four_controls():
    result = _manual_aws_placeholder()
    assert {r["control_id"] for r in result} == {"AC-001", "LOG-001", "DATA-001", "BCP-001"}
    assert all(r["status"] == "unknown" for r in result)


def test_github_checks_returns_unknown_when_repo_unreachable(monkeypatch):
    routes = {"repos/o/r": FakeResponse(404, {"message": "Not Found"})}
    monkeypatch.setattr(github_checks.httpx, "AsyncClient", fake_client_factory(routes))

    result = asyncio.run(run_github_checks("token", "o", "r"))
    assert len(result) == 1
    assert result[0]["control_id"] == "CM-002"
    assert result[0]["status"] == "unknown"
    assert "404" in result[0]["summary"]


def test_github_checks_pass_when_protected_with_reviews(monkeypatch):
    routes = {
        "repos/o/r": FakeResponse(200, {"default_branch": "main", "full_name": "o/r", "private": True}),
        "branches/main/protection": FakeResponse(
            200, {"required_pull_request_reviews": {"required_approving_review_count": 1}}
        ),
        "actions/permissions": FakeResponse(200, {}),
        "code-scanning/alerts": FakeResponse(200, []),
    }
    monkeypatch.setattr(github_checks.httpx, "AsyncClient", fake_client_factory(routes))

    by_id = {r["control_id"]: r for r in asyncio.run(run_github_checks("token", "o", "r"))}
    assert by_id["CM-001"]["status"] == "pass"
    assert by_id["CM-002"]["status"] == "pass"
    assert by_id["APP-001"]["status"] == "pass"


def test_github_checks_fail_when_reviews_missing(monkeypatch):
    routes = {
        "repos/o/r": FakeResponse(200, {"default_branch": "main"}),
        "branches/main/protection": FakeResponse(200, {}),
        "actions/permissions": FakeResponse(200, {}),
        "code-scanning/alerts": FakeResponse(404, {}),
    }
    monkeypatch.setattr(github_checks.httpx, "AsyncClient", fake_client_factory(routes))

    by_id = {r["control_id"]: r for r in asyncio.run(run_github_checks("token", "o", "r"))}
    assert by_id["CM-001"]["status"] == "fail"
    assert by_id["APP-001"]["status"] == "unknown"

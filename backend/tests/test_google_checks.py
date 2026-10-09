import json

import pytest

from app.services.integrations import google_checks


class FakeResponse:
    def __init__(self, status_code: int, payload: dict):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload

    @property
    def text(self):
        return json.dumps(self._payload)


class FakeClient:
    def __init__(self, response: FakeResponse):
        self._response = response

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def get(self, url, headers=None, params=None):
        return self._response


def _install(monkeypatch, users, status_code=200):
    response = FakeResponse(status_code, {"users": users})
    monkeypatch.setattr(google_checks.httpx, "Client", lambda *a, **k: FakeClient(response))
    monkeypatch.setattr(google_checks, "_get_access_token", lambda sa, subject: "fake-token")


def _run(users=None, status_code=200, monkeypatch=None):
    _install(monkeypatch, users or [], status_code)
    return google_checks.run_google_workspace_checks(
        "admin@acme.com", '{"type": "service_account"}', "admin@acme.com"
    )


def _by_id(results):
    return {r["control_id"]: r for r in results}


def test_guided_fallback_without_service_account():
    results = _by_id(google_checks.run_google_workspace_checks("admin@acme.com"))
    assert results["AC-001"]["status"] == "unknown"
    assert results["AC-002"]["status"] == "unknown"
    assert "admin@acme.com" in results["AC-001"]["summary"]


def test_live_checks_pass_when_all_admins_enrolled(monkeypatch):
    users = [
        {"primaryEmail": "alice@acme.com", "isAdmin": True, "isEnforcedIn2Sv": True},
        {"primaryEmail": "dev@acme.com", "isAdmin": False, "isEnforcedIn2Sv": True},
    ]
    results = _by_id(_run(users, monkeypatch=monkeypatch))
    assert results["AC-001"]["status"] == "pass"
    assert results["AC-002"]["status"] == "pass"
    assert results["AC-001"]["evidence"]["admin_count"] == 1


def test_live_checks_fail_when_admin_missing_2sv(monkeypatch):
    users = [
        {"primaryEmail": "admin@acme.com", "isAdmin": True, "isEnforcedIn2Sv": False},
    ]
    results = _by_id(_run(users, monkeypatch=monkeypatch))
    assert results["AC-001"]["status"] == "fail"
    assert results["AC-001"]["evidence"]["admins_missing_2sv"] == ["admin@acme.com"]


def test_live_checks_fail_on_generic_admin_mailbox(monkeypatch):
    users = [
        {"primaryEmail": "it@acme.com", "isAdmin": True, "isEnforcedIn2Sv": True},
    ]
    results = _by_id(_run(users, monkeypatch=monkeypatch))
    assert results["AC-001"]["status"] == "pass"
    assert results["AC-002"]["status"] == "fail"
    assert results["AC-002"]["evidence"]["generic_admins"] == ["it@acme.com"]


def test_live_checks_directory_error(monkeypatch):
    results = _by_id(_run([], status_code=403, monkeypatch=monkeypatch))
    assert results["AC-001"]["status"] == "unknown"
    assert "HTTP 403" in results["AC-001"]["summary"]


def test_live_checks_auth_failure_reported(monkeypatch):
    def boom(sa, subject):
        raise RuntimeError("invalid_grant")

    monkeypatch.setattr(google_checks, "_get_access_token", boom)
    results = _by_id(
        google_checks.run_google_workspace_checks(
            "admin@acme.com", '{"type": "service_account"}', "admin@acme.com"
        )
    )
    assert results["AC-001"]["status"] == "unknown"
    assert "live scan failed" in results["AC-001"]["summary"]


def test_connect_google_with_service_account_uses_live_scan(client, register, monkeypatch):
    _install(
        monkeypatch,
        [{"primaryEmail": "alice@acme.com", "isAdmin": True, "isEnforcedIn2Sv": True}],
    )
    user = register()
    resp = client.post(
        "/api/integrations/google",
        json={
            "admin_email": "alice@acme.com",
            "service_account_json": '{"type": "service_account"}',
            "impersonate_email": "alice@acme.com",
        },
        headers=user["headers"],
    )
    assert resp.status_code == 200, resp.text

    controls = {c["control_id"]: c for c in client.get("/api/controls", headers=user["headers"]).json()}
    assert controls["AC-001"]["status"] == "pass"
    assert controls["AC-002"]["status"] == "pass"

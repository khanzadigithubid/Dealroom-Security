import pytest

from app.services.scan_runner import _map_status
from app.models.entities import CheckStatus


def test_status_mapping():
    assert _map_status("pass") == CheckStatus.pass_
    assert _map_status("fail") == CheckStatus.fail
    assert _map_status("not_applicable") == CheckStatus.not_applicable
    assert _map_status("something-else") == CheckStatus.unknown


def test_list_integrations_empty(client, register):
    user = register()
    resp = client.get("/api/integrations", headers=user["headers"])
    assert resp.status_code == 200
    assert resp.json() == []


def test_connect_google_runs_stub_checks(client, register):
    user = register()
    resp = client.post(
        "/api/integrations/google",
        json={"admin_email": "admin@example.com", "label": "Google Workspace"},
        headers=user["headers"],
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["connected"] is True

    integrations = client.get("/api/integrations", headers=user["headers"]).json()
    assert [i["kind"] for i in integrations] == ["google_workspace"]

    controls = {c["control_id"]: c for c in client.get("/api/controls", headers=user["headers"]).json()}
    assert controls["AC-001"]["status"] == "unknown"
    assert controls["AC-002"]["status"] == "unknown"
    assert "admin@example.com" in controls["AC-001"]["summary"]
    assert "Not scanned yet" not in controls["AC-001"]["summary"]


def test_connect_github_uses_scan_results(client, register, monkeypatch):
    async def fake_github_checks(token, owner, repo):
        assert (token, owner, repo) == ("tok", "acme", "api")
        return [
            {"control_id": "CM-001", "status": "pass", "summary": "protected", "evidence": {"a": 1}},
            {"control_id": "CM-002", "status": "pass", "summary": "repo ok", "evidence": {}},
            {"control_id": "APP-001", "status": "fail", "summary": "no scanning", "evidence": {}},
        ]

    monkeypatch.setattr("app.services.scan_runner.run_github_checks", fake_github_checks)

    user = register()
    resp = client.post(
        "/api/integrations/github",
        json={"token": "tok", "owner": "acme", "repo": "api", "label": "GitHub production"},
        headers=user["headers"],
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["label"] == "GitHub production"

    controls = {c["control_id"]: c for c in client.get("/api/controls", headers=user["headers"]).json()}
    assert controls["CM-001"]["status"] == "pass"
    assert controls["CM-002"]["status"] == "pass"
    assert controls["APP-001"]["status"] == "fail"
    assert controls["CM-001"]["summary"] == "protected"
    assert controls["CM-001"]["updated_at"] is not None


def test_trigger_scan_returns_control_count(client, register, monkeypatch):
    async def fake_github_checks(token, owner, repo):
        return [
            {"control_id": "CM-001", "status": "pass", "summary": "x", "evidence": {}},
            {"control_id": "CM-002", "status": "pass", "summary": "y", "evidence": {}},
        ]

    monkeypatch.setattr("app.services.scan_runner.run_github_checks", fake_github_checks)

    user = register()
    client.post(
        "/api/integrations/github",
        json={"token": "tok", "owner": "acme", "repo": "api"},
        headers=user["headers"],
    )
    resp = client.post("/api/integrations/scan", headers=user["headers"])
    assert resp.status_code == 200
    assert resp.json()["scanned_controls"] == 2


def test_integrations_require_auth(client):
    assert client.get("/api/integrations").status_code == 401
    assert client.post("/api/integrations/scan").status_code == 401


def test_connect_github_does_not_scan_without_credentials(client, register):
    user = register()
    resp = client.post(
        "/api/integrations/github",
        json={"token": "", "owner": "", "repo": "", "label": "GitHub"},
        headers=user["headers"],
    )
    assert resp.status_code == 200
    controls = {c["control_id"]: c for c in client.get("/api/controls", headers=user["headers"]).json()}
    assert controls["CM-001"]["status"] == "unknown"


@pytest.mark.parametrize("path", ["/api/controls", "/api/integrations", "/api/org", "/api/questionnaires"])
def test_protected_endpoints_reject_bad_token(client, path):
    resp = client.get(path, headers={"Authorization": "Bearer not-a-real-token"})
    assert resp.status_code == 401

from app.services.answer_builder import build_draft_for_question  # noqa: F401  (import smoke)


def test_trust_page_requires_existing_slug(client):
    resp = client.get("/api/trust/does-not-exist")
    assert resp.status_code == 404


def test_trust_page_public_and_empty_before_scan(client, register):
    user = register(company_name="Acme Corp")
    org = client.get("/api/org", headers=user["headers"]).json()

    resp = client.get(f"/api/trust/{org['slug']}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["company_name"] == "Acme Corp"
    assert body["slug"] == "acme-corp"
    assert body["trust_blurb"]
    assert body["controls"] == []


def test_trust_page_lists_scanned_controls(client, register):
    user = register(company_name="Acme Corp")
    org = client.get("/api/org", headers=user["headers"]).json()

    client.post(
        "/api/integrations/google",
        json={"admin_email": "admin@acme.com"},
        headers=user["headers"],
    )

    body = client.get(f"/api/trust/{org['slug']}").json()
    ids = {c["control_id"] for c in body["controls"]}
    assert ids == {"AC-001", "AC-002"}
    for control in body["controls"]:
        assert control["status"] in {"pass", "fail", "unknown", "not_applicable"}
        assert "pass_" not in control["status"]

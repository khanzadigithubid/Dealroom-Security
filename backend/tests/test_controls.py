from app.data.control_catalog import CONTROL_CATALOG


def test_controls_require_auth(client):
    assert client.get("/api/controls").status_code == 401


def test_controls_return_full_catalog_as_unknown_for_fresh_org(client, register):
    user = register()
    resp = client.get("/api/controls", headers=user["headers"])
    assert resp.status_code == 200, resp.text
    controls = resp.json()
    assert len(controls) == len(CONTROL_CATALOG) == 10
    for control in controls:
        assert control["status"] == "unknown"
        assert control["title"]
        assert control["category"]
        assert "Not scanned yet" in control["summary"]
        assert control["updated_at"] is None


def test_control_ids_are_unique(client, register):
    user = register()
    controls = client.get("/api/controls", headers=user["headers"]).json()
    ids = [c["control_id"] for c in controls]
    assert len(ids) == len(set(ids))

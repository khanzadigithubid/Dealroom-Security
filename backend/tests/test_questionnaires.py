import io

SAMPLE_CSV = (
    "question\n"
    "Do you enforce multi-factor authentication for administrative access?\n"
    "Is your default production branch protected with required code reviews?\n"
    "Do you maintain audit logging for cloud infrastructure?\n"
    "Is customer data encrypted at rest in object storage?\n"
    "Do you use version control for all production code changes?\n"
    "Do you maintain a list of subprocessors and third-party vendors?\n"
    "Do you have a documented incident response process?\n"
    "Do you perform application security testing before release?\n"
    "Do you maintain backups and tested recovery for critical data?\n"
)


def upload(client, headers, content=SAMPLE_CSV, filename="buyer.csv", title="Acme Q4"):
    files = {"file": (filename, io.BytesIO(content.encode("utf-8")), "text/csv")}
    data = {"title": title, "buyer_name": "Acme Corporation"}
    return client.post("/api/questionnaires/upload", files=files, data=data, headers=headers)


def test_upload_parses_questions_and_drafts_answers(client, register):
    user = register()
    resp = upload(client, user["headers"])
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["question_count"] == 9
    assert body["title"] == "Acme Q4"
    assert body["buyer_name"] == "Acme Corporation"

    questions = client.get(
        f"/api/questionnaires/{body['id']}/questions", headers=user["headers"]
    ).json()
    assert len(questions) == 9
    assert [q["row_index"] for q in questions] == list(range(1, 10))
    assert all(q["answer_status"] == "draft" for q in questions)
    assert all(q["draft_text"] for q in questions)

    by_text = {q["question_text"]: q for q in questions}
    assert by_text["Do you enforce multi-factor authentication for administrative access?"][
        "suggested_control_id"
    ] == "AC-001"


def test_upload_rejects_unsupported_extension(client, register):
    user = register()
    resp = upload(client, user["headers"], filename="notes.txt")
    assert resp.status_code == 400
    assert "csv" in resp.text.lower()


def test_upload_rejects_empty_question_file(client, register):
    user = register()
    resp = upload(client, user["headers"], content="question\n\n")
    assert resp.status_code == 400
    assert "no questions" in resp.text.lower()


def test_list_questionnaires(client, register):
    user = register()
    upload(client, user["headers"])
    resp = client.get("/api/questionnaires", headers=user["headers"])
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 1
    assert items[0]["question_count"] == 9


def test_approve_and_export_csv(client, register):
    user = register()
    qid = upload(client, user["headers"]).json()["id"]
    questions = client.get(f"/api/questionnaires/{qid}/questions", headers=user["headers"]).json()
    target = questions[0]

    resp = client.post(
        f"/api/questionnaires/questions/{target['id']}/approve",
        json={"approved_text": "Approved answer text."},
        headers=user["headers"],
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "approved"

    refreshed = client.get(f"/api/questionnaires/{qid}/questions", headers=user["headers"]).json()
    assert refreshed[0]["answer_status"] == "approved"
    assert refreshed[0]["approved_text"] == "Approved answer text."

    export = client.get(f"/api/questionnaires/{qid}/export.csv", headers=user["headers"])
    assert export.status_code == 200
    assert "text/csv" in export.headers["content-type"]
    assert "attachment" in export.headers["content-disposition"]
    lines = export.text.strip().splitlines()
    assert lines[0] == "row,question,control_id,status,answer,evidence"
    assert len(lines) == 10
    assert "Approved answer text." in export.text


def test_approve_falls_back_to_draft_text(client, register):
    user = register()
    qid = upload(client, user["headers"]).json()["id"]
    questions = client.get(f"/api/questionnaires/{qid}/questions", headers=user["headers"]).json()
    target = questions[0]

    resp = client.post(
        f"/api/questionnaires/questions/{target['id']}/approve",
        json={},
        headers=user["headers"],
    )
    assert resp.status_code == 200
    refreshed = client.get(f"/api/questionnaires/{qid}/questions", headers=user["headers"]).json()
    assert refreshed[0]["approved_text"] == target["draft_text"]


def test_approve_unknown_question_returns_404(client, register):
    user = register()
    resp = client.post(
        "/api/questionnaires/questions/99999/approve",
        json={},
        headers=user["headers"],
    )
    assert resp.status_code == 404


def test_regenerate_rebuilds_drafts(client, register):
    user = register()
    qid = upload(client, user["headers"]).json()["id"]
    resp = client.post(f"/api/questionnaires/{qid}/regenerate", headers=user["headers"])
    assert resp.status_code == 200
    assert resp.json()["regenerated"] == 9


def test_questionnaires_are_isolated_per_organization(client, register):
    owner = register(email="owner@example.com")
    stranger = register(email="stranger@example.com")
    qid = upload(client, owner["headers"]).json()["id"]

    assert (
        client.get(f"/api/questionnaires/{qid}/questions", headers=stranger["headers"]).status_code
        == 404
    )
    assert client.get(f"/api/questionnaires/{qid}/export.csv", headers=stranger["headers"]).status_code == 404
    assert client.post(f"/api/questionnaires/{qid}/regenerate", headers=stranger["headers"]).status_code == 404
    assert client.get("/api/questionnaires", headers=stranger["headers"]).json() == []


def test_upload_requires_auth(client):
    files = {"file": ("buyer.csv", io.BytesIO(SAMPLE_CSV.encode()), "text/csv")}
    assert client.post("/api/questionnaires/upload", files=files, data={"title": "x"}).status_code == 401

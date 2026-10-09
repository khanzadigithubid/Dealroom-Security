import json

from sqlalchemy.orm import Session

from app.data.control_catalog import catalog_by_id
from app.models.entities import Answer, AnswerStatus, CheckStatus, ControlCheck, Question


def build_draft_for_question(db: Session, org_id: int, question: Question) -> Answer:
    catalog = catalog_by_id()
    control_id = question.suggested_control_id
    if not control_id:
        draft = (
            "We address this control through our security program. "
            "Please connect integrations or map this question to a control for auto-generated evidence."
        )
        evidence_refs = "[]"
    else:
        check = (
            db.query(ControlCheck)
            .filter(ControlCheck.organization_id == org_id, ControlCheck.control_id == control_id)
            .first()
        )
        definition = catalog.get(control_id)
        if not definition:
            draft = "Control mapping pending review."
            evidence_refs = "[]"
        elif not check:
            draft = definition.unknown_answer
            evidence_refs = json.dumps([{"control_id": control_id, "status": "unknown"}])
        elif check.status == CheckStatus.pass_:
            draft = definition.pass_answer
            evidence_refs = json.dumps(
                [{"control_id": control_id, "status": "pass", "summary": check.summary}]
            )
        elif check.status == CheckStatus.fail:
            draft = definition.fail_answer
            evidence_refs = json.dumps(
                [{"control_id": control_id, "status": "fail", "summary": check.summary}]
            )
        else:
            draft = definition.unknown_answer
            evidence_refs = json.dumps(
                [{"control_id": control_id, "status": check.status.value, "summary": check.summary}]
            )

    answer = question.answer
    if not answer:
        answer = Answer(question_id=question.id)
        db.add(answer)
    answer.draft_text = draft
    answer.status = AnswerStatus.draft
    answer.evidence_refs = evidence_refs
    db.commit()
    db.refresh(answer)
    return answer

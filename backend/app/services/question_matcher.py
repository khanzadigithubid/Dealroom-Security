from app.data.control_catalog import CONTROL_CATALOG, ControlDefinition


def score_control(question: str, control: ControlDefinition) -> int:
    q = question.lower()
    score = 0
    for kw in control.keywords:
        if kw in q:
            score += 3
    for token in control.title.lower().split():
        if len(token) > 4 and token in q:
            score += 1
    return score


def suggest_control_id(question_text: str) -> str | None:
    best: ControlDefinition | None = None
    best_score = 0
    for control in CONTROL_CATALOG:
        s = score_control(question_text, control)
        if s > best_score:
            best_score = s
            best = control
    if best_score < 3 or best is None:
        return None
    return best.id

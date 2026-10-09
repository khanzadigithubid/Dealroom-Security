import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, getToken } from "../api";
import PageHeader from "../components/PageHeader";

export default function QuestionnaireDetail() {
  const { id } = useParams();
  const qid = Number(id);
  const [questions, setQuestions] = useState<
    Array<{
      id: number;
      row_index: number;
      question_text: string;
      suggested_control_id: string | null;
      answer_status: string | null;
      draft_text: string | null;
      approved_text: string | null;
    }>
  >([]);

  async function load() {
    setQuestions(await api.questions(qid));
  }

  useEffect(() => {
    if (qid) load();
  }, [qid]);

  const approvedCount = useMemo(() => questions.filter((q) => q.answer_status === "approved").length, [questions]);

  async function approve(questionId: number, draft: string | null) {
    await api.approve(questionId, draft || undefined);
    load();
  }

  async function regenerate() {
    await api.regenerate(qid);
    load();
  }

  async function exportCsv() {
    const token = getToken();
    const res = await fetch(`/api/questionnaires/${qid}/export.csv`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    if (!res.ok) throw new Error("Export failed");
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `dealroom-export-${qid}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div>
      <PageHeader
        breadcrumb={
          <Link to="/questionnaires" className="breadcrumb-link">
            ← Back to questionnaires
          </Link>
        }
        title="Review answers"
        description="Approve each draft before exporting to the buyer."
        actions={
          <>
            <button type="button" className="btn btn-secondary" onClick={regenerate}>
              Regenerate from scans
            </button>
            <button type="button" className="btn btn-primary" onClick={() => exportCsv().catch(console.error)}>
              Export CSV
            </button>
          </>
        }
      />

      {questions.length > 0 && (
        <div className="review-summary">
          <span>
            <strong>{approvedCount}</strong> / {questions.length} approved
          </span>
          <span className="muted">Export when all critical answers are approved.</span>
        </div>
      )}

      <div className="qa-list">
        {questions.map((q) => {
          const isApproved = q.answer_status === "approved";
          return (
            <article key={q.id} className={`card qa-item${isApproved ? " qa-approved" : ""}`}>
              <div className="qa-meta">
                <span className="mono">Q{q.row_index}</span>
                {q.suggested_control_id && <span className="badge">{q.suggested_control_id}</span>}
                {isApproved && <span className="badge pass">Approved</span>}
              </div>
              <h3>{q.question_text}</h3>
              <div className="answer-box">{q.approved_text || q.draft_text}</div>
              {!isApproved && (
                <div className="qa-actions">
                  <button type="button" className="btn btn-primary btn-sm" onClick={() => approve(q.id, q.draft_text)}>
                    Approve answer
                  </button>
                </div>
              )}
            </article>
          );
        })}
      </div>
    </div>
  );
}

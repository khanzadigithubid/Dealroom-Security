import { FormEvent, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import PageHeader from "../components/PageHeader";

export default function QuestionnairesPage() {
  const [list, setList] = useState<
    Array<{ id: number; title: string; buyer_name: string; uploaded_at: string; question_count: number }>
  >([]);
  const [error, setError] = useState("");

  async function load() {
    setList(await api.questionnaires());
  }

  useEffect(() => {
    load();
  }, []);

  async function onUpload(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError("");
    const form = e.currentTarget;
    const fd = new FormData(form);
    try {
      await api.uploadQuestionnaire(fd);
      form.reset();
      load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    }
  }

  return (
    <div>
      <PageHeader
        title="Questionnaires"
        description="Upload the buyer's security assessment — one question per row in column A (.csv or .xlsx)."
      />

      <form className="card stack" onSubmit={onUpload} style={{ marginBottom: "1.5rem" }}>
        <div>
          <h2 className="card-title">New assessment</h2>
          <p className="card-sub">We match questions to controls and draft answers from your latest scan.</p>
        </div>
        <div className="row-fields">
          <label className="field">
            <span className="field-label">Title</span>
            <input name="title" required placeholder="Acme Corp — Q4 security review" />
          </label>
          <label className="field">
            <span className="field-label">Buyer name</span>
            <input name="buyer_name" placeholder="Acme Corporation" />
          </label>
        </div>
        <label className="field">
          <span className="field-label">Question file</span>
          <div className="file-drop">
            <div className="file-drop-title">Drop CSV or Excel here</div>
            <div className="file-drop-hint">Column A = question text · try sample-data/buyer-questionnaire.csv</div>
            <input name="file" type="file" accept=".csv,.xlsx" required style={{ marginTop: "0.75rem" }} />
          </div>
        </label>
        {error && <p className="alert alert-error">{error}</p>}
        <button type="submit" className="btn btn-primary" style={{ alignSelf: "flex-start" }}>
          Upload &amp; generate drafts
        </button>
      </form>

      <div className="card table-card">
        {list.length === 0 ? (
          <div className="empty-state">No questionnaires yet — upload your first buyer file above.</div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Title</th>
                <th>Buyer</th>
                <th>Questions</th>
                <th>Uploaded</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {list.map((q) => (
                <tr key={q.id}>
                  <td className="cell-title">{q.title}</td>
                  <td>{q.buyer_name || "—"}</td>
                  <td>{q.question_count}</td>
                  <td className="cell-muted">{new Date(q.uploaded_at).toLocaleString()}</td>
                  <td>
                    <Link to={`/questionnaires/${q.id}`}>Review answers →</Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

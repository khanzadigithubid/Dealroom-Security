import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import PageHeader from "../components/PageHeader";

export default function Dashboard() {
  const [org, setOrg] = useState<{ name: string; slug: string } | null>(null);
  const [stats, setStats] = useState({ pass: 0, fail: 0, unknown: 0, total: 10, questionnaires: 0 });

  useEffect(() => {
    Promise.all([api.org(), api.controls(), api.questionnaires()]).then(([o, controls, qs]) => {
      setOrg({ name: o.name, slug: o.slug });
      setStats({
        pass: controls.filter((c) => c.status === "pass").length,
        fail: controls.filter((c) => c.status === "fail").length,
        unknown: controls.filter((c) => c.status === "unknown").length,
        total: controls.length,
        questionnaires: qs.length,
      });
    });
  }, []);

  const verified = stats.pass + stats.fail;
  const pct = stats.total ? Math.round((verified / stats.total) * 100) : 0;

  return (
    <div>
      <PageHeader
        title={org ? org.name : "Overview"}
        description="Track control readiness and questionnaire progress for your next enterprise deal."
      />

      <div className="progress-block card">
        <div className="progress-head">
          <span>Control verification progress</span>
          <span>{pct}% scanned</span>
        </div>
        <div className="progress-track">
          <div className="progress-fill" style={{ width: `${pct}%` }} />
        </div>
      </div>

      <div className="stat-row">
        <div className="card stat-card stat-pass">
          <span className="stat-label">Passing</span>
          <span className="stat-value">{stats.pass}</span>
        </div>
        <div className="card stat-card stat-fail">
          <span className="stat-label">Needs remediation</span>
          <span className="stat-value">{stats.fail}</span>
        </div>
        <div className="card stat-card">
          <span className="stat-label">Not verified</span>
          <span className="stat-value">{stats.unknown}</span>
        </div>
        <div className="card stat-card stat-primary">
          <span className="stat-label">Questionnaires</span>
          <span className="stat-value">{stats.questionnaires}</span>
        </div>
      </div>

      <h2 style={{ fontSize: "1.1rem", marginBottom: "0.75rem" }}>Get started</h2>
      <div className="action-grid">
        <Link to="/integrations" className="card action-card">
          <span className="action-step">Step 1</span>
          <h3>Connect integrations</h3>
          <p>Link GitHub, AWS, or Google to pull live evidence.</p>
        </Link>
        <Link to="/controls" className="card action-card">
          <span className="action-step">Step 2</span>
          <h3>Review controls</h3>
          <p>See pass/fail status across your security program.</p>
        </Link>
        <Link to="/questionnaires" className="card action-card">
          <span className="action-step">Step 3</span>
          <h3>Upload questionnaire</h3>
          <p>Import buyer CSV/XLSX and approve auto-drafted answers.</p>
        </Link>
      </div>

      {org && (
        <p className="muted" style={{ marginTop: "1.5rem" }}>
          Share your{" "}
          <a href={`/trust/${org.slug}`} target="_blank" rel="noreferrer">
            public trust center
          </a>{" "}
          with procurement teams.
        </p>
      )}
    </div>
  );
}

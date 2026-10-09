import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../api";
import { IconShield } from "../components/icons";

export default function TrustPage() {
  const { slug } = useParams();
  const [data, setData] = useState<Awaited<ReturnType<typeof api.trust>> | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!slug) return;
    api
      .trust(slug)
      .then(setData)
      .catch((e) => setError(e instanceof Error ? e.message : "Not found"));
  }, [slug]);

  if (error) {
    return (
      <div className="trust-page">
        <div className="trust-body">
          <p className="alert alert-error">{error}</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="trust-page">
        <div className="trust-body muted">Loading trust center…</div>
      </div>
    );
  }

  return (
    <div className="trust-page">
      <header className="trust-hero">
        <div className="trust-hero-inner">
          <span className="auth-hero-badge" style={{ margin: "0 auto 1rem" }}>
            <IconShield className="auth-feature-icon" />
            Security &amp; compliance
          </span>
          <h1>{data.company_name}</h1>
          <p className="page-head-desc" style={{ margin: "0 auto" }}>
            {data.trust_blurb}
          </p>
        </div>
      </header>
      <section className="trust-body">
        <h2 style={{ fontSize: "1.15rem", marginBottom: "1rem" }}>Control status</h2>
        {data.controls.length === 0 ? (
          <div className="card empty-state">Control scan results will appear here once integrations are connected.</div>
        ) : (
          <div className="trust-grid">
            {data.controls.map((c) => (
              <article key={c.control_id} className="card trust-card">
                <span className={`badge ${c.status === "pass" ? "pass" : c.status === "fail" ? "fail" : "unknown"}`}>
                  {c.status}
                </span>
                <h3>{c.title}</h3>
                <p className="cell-muted">{c.summary}</p>
              </article>
            ))}
          </div>
        )}
      </section>
      <footer className="trust-footer">Powered by DealRoom Security</footer>
    </div>
  );
}

import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, setToken } from "../api";
import { IconShield } from "../components/icons";

export default function AuthPage() {
  const navigate = useNavigate();
  const [mode, setMode] = useState<"login" | "register">("register");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError("");
    setLoading(true);
    const fd = new FormData(e.currentTarget);
    const email = String(fd.get("email") || "");
    const password = String(fd.get("password") || "");
    try {
      if (mode === "login") {
        const { access_token } = await api.login(email, password);
        setToken(access_token);
      } else {
        const full_name = String(fd.get("full_name") || "");
        const company_name = String(fd.get("company_name") || "");
        const { access_token } = await api.register({ email, password, full_name, company_name });
        setToken(access_token);
      }
      navigate("/");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-page">
      <section className="auth-hero">
        <span className="auth-hero-badge">
          <IconShield className="auth-feature-icon" />
          B2B security questionnaires
        </span>
        <h1>Close enterprise deals faster.</h1>
        <p className="auth-hero-lead">
          Connect your stack, upload the buyer&apos;s Excel, and export evidence-backed answers — built for SaaS teams
          selling internationally.
        </p>
        <ul className="auth-features">
          <li>
            <svg className="auth-feature-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <path d="M20 6 9 17l-5-5" />
            </svg>
            Auto-map questions to SOC-style controls
          </li>
          <li>
            <svg className="auth-feature-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <path d="M20 6 9 17l-5-5" />
            </svg>
            GitHub, AWS &amp; Google Workspace scans
          </li>
          <li>
            <svg className="auth-feature-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <path d="M20 6 9 17l-5-5" />
            </svg>
            Public trust center for buyers
          </li>
        </ul>
      </section>
      <div className="auth-panel-wrap">
        <form className="auth-form" onSubmit={onSubmit}>
          <h2 className="auth-form-title">{mode === "login" ? "Welcome back" : "Create your workspace"}</h2>
          <p className="auth-form-sub">
            {mode === "login" ? "Sign in to continue to DealRoom." : "Free to start — no credit card for MVP."}
          </p>
          <div className="tabs" role="tablist">
            <button type="button" role="tab" className={mode === "register" ? "active" : ""} onClick={() => setMode("register")}>
              Sign up
            </button>
            <button type="button" role="tab" className={mode === "login" ? "active" : ""} onClick={() => setMode("login")}>
              Log in
            </button>
          </div>
          <div className="stack stack-tight">
            {mode === "register" && (
              <>
                <label className="field">
                  <span className="field-label">Full name</span>
                  <input name="full_name" required placeholder="Alex Khan" autoComplete="name" />
                </label>
                <label className="field">
                  <span className="field-label">Company</span>
                  <input name="company_name" required minLength={2} placeholder="Acme SaaS Inc." autoComplete="organization" />
                </label>
              </>
            )}
            <label className="field">
              <span className="field-label">Email</span>
              <input name="email" type="email" required pattern="^[^\s@]+@[^\s@]+\.[^\s@]+$" title="Enter a full email address, e.g. you@company.com" placeholder="you@email.com" autoComplete="email" />
            </label>
            <label className="field">
              <span className="field-label">Password</span>
              <input name="password" type="password" required minLength={8} placeholder="At least 8 characters" autoComplete={mode === "login" ? "current-password" : "new-password"} />
            </label>
            {error && <p className="alert alert-error">{error}</p>}
            <button type="submit" className="btn btn-primary" style={{ width: "100%", marginTop: "0.25rem" }} disabled={loading}>
              {loading ? "Please wait…" : mode === "login" ? "Log in" : "Create workspace"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

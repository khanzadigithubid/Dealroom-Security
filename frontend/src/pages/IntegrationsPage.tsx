import { FormEvent, useEffect, useState } from "react";
import { api } from "../api";
import PageHeader from "../components/PageHeader";

export default function IntegrationsPage() {
  const [message, setMessage] = useState("");
  const [connected, setConnected] = useState<string[]>([]);

  async function refresh() {
    const list = await api.integrations();
    setConnected(list.filter((i) => i.connected).map((i) => i.kind));
  }

  useEffect(() => {
    refresh();
  }, []);

  async function onGitHub(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    setMessage("");
    try {
      await api.connectGitHub({
        token: String(fd.get("token")),
        owner: String(fd.get("owner")),
        repo: String(fd.get("repo")),
      });
      setMessage("GitHub connected — control scan completed.");
      refresh();
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Failed");
    }
  }

  async function onAWS(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    setMessage("");
    try {
      await api.connectAWS({
        access_key_id: String(fd.get("access_key_id")),
        secret_access_key: String(fd.get("secret_access_key")),
        region: String(fd.get("region") || "us-east-1"),
      });
      setMessage("AWS connected. Install boto3 on the backend for full live scans.");
      refresh();
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Failed");
    }
  }

  async function onGoogle(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    setMessage("");
    try {
      const serviceAccount = String(fd.get("service_account_json") || "").trim();
      const impersonate = String(fd.get("impersonate_email") || "").trim();
      await api.connectGoogle({
        admin_email: String(fd.get("admin_email")),
        service_account_json: serviceAccount || undefined,
        impersonate_email: impersonate || undefined,
      });
      setMessage(
        serviceAccount
          ? "Google Workspace connected — live Admin SDK scan completed."
          : "Google Workspace connected — guided checks applied (add a service account for live scans).",
      );
      refresh();
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Failed");
    }
  }

  async function rescan() {
    const r = await api.scan();
    setMessage(`Scan finished — ${r.scanned_controls} control result(s) updated.`);
  }

  return (
    <div>
      <PageHeader
        title="Integrations"
        description="Use read-only credentials where possible. MVP stores secrets locally — encrypt in production."
        actions={
          <button type="button" className="btn btn-secondary" onClick={rescan}>
            Re-run all scans
          </button>
        }
      />
      {message && <div className="alert alert-info">{message}</div>}
      <div className="grid-3">
        <form className="card stack" onSubmit={onGitHub}>
          <div className="integ-card-header">
            <div className="integ-brand">
              <span className="integ-icon github">GH</span>
              <div>
                <div className="card-title" style={{ margin: 0 }}>
                  GitHub
                </div>
                <div className="field-hint">Branch protection &amp; repo</div>
              </div>
            </div>
            {connected.includes("github") && <span className="badge pass">Live</span>}
          </div>
          <label className="field">
            <span className="field-label">Personal access token</span>
            <input name="token" type="password" required placeholder="ghp_…" />
          </label>
          <label className="field">
            <span className="field-label">Owner</span>
            <input name="owner" required placeholder="org-or-user" />
          </label>
          <label className="field">
            <span className="field-label">Repository</span>
            <input name="repo" required placeholder="api-service" />
          </label>
          <button type="submit" className="btn btn-primary">
            Connect &amp; scan
          </button>
        </form>

        <form className="card stack" onSubmit={onAWS}>
          <div className="integ-card-header">
            <div className="integ-brand">
              <span className="integ-icon aws">AWS</span>
              <div>
                <div className="card-title" style={{ margin: 0 }}>
                  Amazon Web Services
                </div>
                <div className="field-hint">Logging &amp; encryption</div>
              </div>
            </div>
            {connected.includes("aws") && <span className="badge pass">Live</span>}
          </div>
          <label className="field">
            <span className="field-label">Access key ID</span>
            <input name="access_key_id" required autoComplete="off" />
          </label>
          <label className="field">
            <span className="field-label">Secret access key</span>
            <input name="secret_access_key" type="password" required autoComplete="off" />
          </label>
          <label className="field">
            <span className="field-label">Region</span>
            <input name="region" defaultValue="us-east-1" />
          </label>
          <button type="submit" className="btn btn-primary">
            Connect
          </button>
        </form>

        <form className="card stack" onSubmit={onGoogle}>
          <div className="integ-card-header">
            <div className="integ-brand">
              <span className="integ-icon google">G</span>
              <div>
                <div className="card-title" style={{ margin: 0 }}>
                  Google Workspace
                </div>
                <div className="field-hint">Identity &amp; MFA</div>
              </div>
            </div>
            {connected.includes("google_workspace") && <span className="badge pass">Live</span>}
          </div>
          <label className="field">
            <span className="field-label">Admin email</span>
            <input name="admin_email" type="email" required placeholder="admin@company.com" />
          </label>
          <label className="field">
            <span className="field-label">Impersonated admin (optional)</span>
            <input name="impersonate_email" type="email" placeholder="admin@company.com" />
            <span className="field-hint">Delegate directory reads as this super-admin.</span>
          </label>
          <label className="field">
            <span className="field-label">Service account JSON (optional)</span>
            <textarea
              name="service_account_json"
              rows={3}
              placeholder='{"type": "service_account", ...}'
            />
            <span className="field-hint">Leave blank for guided checks. Paste a key with domain-wide delegation.</span>
          </label>
          <button type="submit" className="btn btn-primary">
            Connect
          </button>
        </form>
      </div>
    </div>
  );
}

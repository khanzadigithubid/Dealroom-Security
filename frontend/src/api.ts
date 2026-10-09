const TOKEN_KEY = "dealroom_token";

// In dev and Docker the API is same-origin (`/api`), so this defaults to "".
// Set VITE_API_BASE to a full URL (e.g. https://api.example.com) for split deployments.
const API_BASE = (import.meta.env.VITE_API_BASE ?? "").replace(/\/+$/, "");

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string | null) {
  if (token) localStorage.setItem(TOKEN_KEY, token);
  else localStorage.removeItem(TOKEN_KEY);
}

const FIELD_LABELS: Record<string, string> = {
  email: "Email",
  password: "Password",
  full_name: "Full name",
  company_name: "Company",
  username: "Email",
};

export function formatDetail(detail: unknown): string {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    const issues = detail as Array<{
      type?: string;
      loc?: unknown[];
      msg?: string;
      ctx?: Record<string, unknown>;
    }>;
    return (
      issues
        .map((issue) => {
          const loc = Array.isArray(issue.loc) ? issue.loc : [];
          const field = String(loc[loc.length - 1] ?? "");
          const label = FIELD_LABELS[field] ?? (field ? field.replace(/_/g, " ") : "");
          let msg = String(issue.msg ?? "is invalid");
          if (issue.type === "string_too_short") {
            msg = `must be at least ${String(issue.ctx?.min_length)} characters`;
          } else if (issue.type === "string_too_long") {
            msg = `must be at most ${String(issue.ctx?.max_length)} characters`;
          } else if (field === "email" && issue.type === "value_error") {
            msg = "must be a valid email address (e.g. you@company.com)";
          }
          return label ? `${label} ${msg}` : msg;
        })
        .filter(Boolean)
        .join(" · ") || "Invalid request"
    );
  }
  if (detail && typeof detail === "object") return JSON.stringify(detail);
  return "Request failed";
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  if (!headers.has("Content-Type") && !(init.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }
  const token = getToken();
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const res = await fetch(`${API_BASE}${path}`, { ...init, headers });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(formatDetail(err.detail));
  }
  if (res.status === 204) return undefined as T;
  const ct = res.headers.get("content-type") || "";
  if (ct.includes("application/json")) return res.json();
  return res.text() as T;
}

export const api = {
  register: (body: { email: string; password: string; full_name: string; company_name: string }) =>
    request<{ access_token: string }>("/api/auth/register", { method: "POST", body: JSON.stringify(body) }),

  login: async (email: string, password: string) => {
    const form = new URLSearchParams();
    form.set("username", email);
    form.set("password", password);
    return request<{ access_token: string }>("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: form,
    });
  },

  me: () => request<{ id: number; email: string; full_name: string }>("/api/auth/me"),
  org: () => request<{ id: number; name: string; slug: string; trust_blurb: string }>("/api/org"),
  controls: () =>
    request<
      Array<{
        control_id: string;
        title: string;
        category: string;
        status: string;
        summary: string;
        updated_at: string | null;
      }>
    >("/api/controls"),
  integrations: () =>
    request<Array<{ id: number; kind: string; label: string; connected: boolean; last_sync_at: string | null }>>(
      "/api/integrations",
    ),
  connectGitHub: (body: { token: string; owner: string; repo: string; label?: string }) =>
    request("/api/integrations/github", { method: "POST", body: JSON.stringify(body) }),
  connectAWS: (body: { access_key_id: string; secret_access_key: string; region?: string; label?: string }) =>
    request("/api/integrations/aws", { method: "POST", body: JSON.stringify(body) }),
  connectGoogle: (body: {
    admin_email: string;
    service_account_json?: string;
    impersonate_email?: string;
    label?: string;
  }) => request("/api/integrations/google", { method: "POST", body: JSON.stringify(body) }),
  scan: () => request<{ scanned_controls: number }>("/api/integrations/scan", { method: "POST" }),
  questionnaires: () =>
    request<Array<{ id: number; title: string; buyer_name: string; uploaded_at: string; question_count: number }>>(
      "/api/questionnaires",
    ),
  uploadQuestionnaire: (form: FormData) =>
    request<{ id: number; title: string; buyer_name: string; uploaded_at: string; question_count: number }>(
      "/api/questionnaires/upload",
      { method: "POST", body: form },
    ),
  questions: (id: number) =>
    request<
      Array<{
        id: number;
        row_index: number;
        question_text: string;
        suggested_control_id: string | null;
        answer_status: string | null;
        draft_text: string | null;
        approved_text: string | null;
      }>
    >(`/api/questionnaires/${id}/questions`),
  regenerate: (id: number) => request(`/api/questionnaires/${id}/regenerate`, { method: "POST" }),
  approve: (questionId: number, approved_text?: string) =>
    request(`/api/questionnaires/questions/${questionId}/approve`, {
      method: "POST",
      body: JSON.stringify({ approved_text: approved_text ?? null }),
    }),
  trust: (slug: string) =>
    request<{
      company_name: string;
      slug: string;
      trust_blurb: string;
      controls: Array<{
        control_id: string;
        title: string;
        category: string;
        status: string;
        summary: string;
      }>;
    }>(`/api/trust/${slug}`),
};

import { NavLink, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { api, setToken } from "../api";
import { IconExternal, IconFile, IconGrid, IconLogout, IconPlug, IconShield } from "./icons";

const nav = [
  { to: "/", label: "Overview", icon: IconGrid, end: true },
  { to: "/integrations", label: "Integrations", icon: IconPlug },
  { to: "/controls", label: "Controls", icon: IconShield },
  { to: "/questionnaires", label: "Questionnaires", icon: IconFile },
];

export default function AppShell({ children }: { children: React.ReactNode }) {
  const navigate = useNavigate();
  const [org, setOrg] = useState<{ name: string; slug: string } | null>(null);
  const [userEmail, setUserEmail] = useState("");

  useEffect(() => {
    api.org().then((o) => setOrg({ name: o.name, slug: o.slug })).catch(() => setOrg(null));
    api.me().then((u) => setUserEmail(u.email)).catch(() => setUserEmail(""));
  }, []);

  function logout() {
    setToken(null);
    navigate("/login");
  }

  return (
    <div className="shell">
      <aside className="shell-sidebar">
        <div className="shell-brand">
          <div className="shell-logo" aria-hidden>
            DR
          </div>
          <div>
            <div className="shell-brand-title">DealRoom</div>
            <div className="shell-brand-sub">Security</div>
          </div>
        </div>

        {org && (
          <div className="shell-org">
            <span className="shell-org-label">Workspace</span>
            <strong>{org.name}</strong>
          </div>
        )}

        <nav className="shell-nav" aria-label="Main">
          {nav.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) => `shell-nav-link${isActive ? " is-active" : ""}`}
            >
              <Icon className="shell-nav-icon" />
              {label}
            </NavLink>
          ))}
          {org && (
            <a className="shell-nav-link shell-nav-external" href={`/trust/${org.slug}`} target="_blank" rel="noreferrer">
              <IconExternal className="shell-nav-icon" />
              Trust center
            </a>
          )}
        </nav>

        <div className="shell-footer">
          {userEmail && <span className="shell-user">{userEmail}</span>}
          <button type="button" className="btn btn-ghost btn-sm shell-logout" onClick={logout}>
            <IconLogout className="shell-nav-icon" />
            Log out
          </button>
        </div>
      </aside>
      <div className="shell-main">
        <div className="shell-content">{children}</div>
      </div>
    </div>
  );
}

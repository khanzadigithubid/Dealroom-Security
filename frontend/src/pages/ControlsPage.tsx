import { useEffect, useState } from "react";
import { api } from "../api";
import PageHeader from "../components/PageHeader";

export default function ControlsPage() {
  const [controls, setControls] = useState<
    Array<{ control_id: string; title: string; category: string; status: string; summary: string }>
  >([]);

  useEffect(() => {
    api.controls().then(setControls);
  }, []);

  return (
    <div>
      <PageHeader
        title="Controls"
        description="Mapped to common enterprise security assessments. Connect integrations and re-scan to update evidence."
      />
      <div className="card table-card">
        <table className="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Category</th>
              <th>Control</th>
              <th>Status</th>
              <th>Evidence summary</th>
            </tr>
          </thead>
          <tbody>
            {controls.map((c) => (
              <tr key={c.control_id}>
                <td className="mono">{c.control_id}</td>
                <td>{c.category}</td>
                <td className="cell-title">{c.title}</td>
                <td>
                  <span className={`badge ${c.status === "pass" ? "pass" : c.status === "fail" ? "fail" : "unknown"}`}>
                    {c.status}
                  </span>
                </td>
                <td className="cell-muted">{c.summary}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

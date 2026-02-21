import type { VerdictCase } from "../types";

interface CaseSelectorProps {
  cases: VerdictCase[];
  onSelect: (c: VerdictCase) => void;
}

const aggressionColor: Record<string, string> = {
  Low: "#22c55e",
  Medium: "#f59e0b",
  High: "#ef4444",
};

export default function CaseSelector({ cases, onSelect }: CaseSelectorProps) {
  return (
    <div className="case-selector">
      <header className="case-selector-header">
        <div className="logo-mark">V</div>
        <div>
          <h1>VERDICT</h1>
          <p className="subtitle">AI Deposition Interrogation System</p>
        </div>
      </header>

      <p className="instruction">Select a case to begin the deposition session.</p>

      <div className="case-grid">
        {cases.map((c) => {
          const witness = c.witness_name.split(";")[0].trim();
          return (
            <button
              key={c.id}
              className="case-card"
              onClick={() => onSelect(c)}
            >
              <div className="case-card-header">
                <span
                  className="aggression-badge"
                  style={{ backgroundColor: aggressionColor[c.aggression_level] }}
                >
                  {c.aggression_level}
                </span>
                <span className="case-type-label">{c.case_type}</span>
              </div>
              <h3 className="case-title">{c.case_name}</h3>
              <div className="case-meta">
                <div className="meta-row">
                  <span className="meta-label">Witness</span>
                  <span className="meta-value">{witness}</span>
                </div>
                <div className="meta-row">
                  <span className="meta-label">Date</span>
                  <span className="meta-value">{c.deposition_date}</span>
                </div>
              </div>
              <p className="case-focus">{c.focus_areas.split(";")[0].trim()}</p>
            </button>
          );
        })}
      </div>
    </div>
  );
}

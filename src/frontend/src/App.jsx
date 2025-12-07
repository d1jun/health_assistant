import useSWR from "swr";

const fetcher = async (url) => {
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error("Failed to fetch dashboard data");
  }
  return res.json();
};

const MetricPill = ({ label, value }) => (
  <div className="pill">
    <div className="pill-label">{label}</div>
    <div className="pill-value">{value.toFixed(1)} / 100</div>
  </div>
);

const AnomalyList = ({ anomalies }) => {
  if (!anomalies?.length) {
    return <div className="muted">No strong anomalies detected.</div>;
  }
  return (
    <ul className="anomaly-list">
      {anomalies.map((item) => (
        <li key={item.metric} className="anomaly-card">
          <div className="anomaly-metric">{item.metric}</div>
          <div className="anomaly-body">
            <span className={`badge ${item.direction === "higher" ? "badge-warm" : "badge-cool"}`}>
              {item.direction} vs baseline
            </span>
            <div className="muted">
              value {item.value.toFixed(0)} vs baseline {item.baseline_mean.toFixed(0)} (z {item.z_score.toFixed(1)})
            </div>
          </div>
        </li>
      ))}
    </ul>
  );
};

function App() {
  const { data, error, isLoading } = useSWR("/api/summary", fetcher);

  const metrics = data?.normalized_metrics ?? {};
  const anomalies = data?.anomalies ?? [];
  const suggestion = data?.suggestion?.text;

  return (
    <div className="page">
      <div className="glow glow-a" />
      <div className="glow glow-b" />
      <header className="hero">
        <div>
          <div className="eyebrow">Personal Wellness Overview</div>
          <h1>Weekly Health Pulse</h1>
          <p className="muted">
            Aggregated view of your exercise, sleep, nutrition, and recovery signals.
          </p>
          {data?.week_range && (
            <div className="muted small">
              Window: {data.week_range.start} → {data.week_range.end}
            </div>
          )}
        </div>
        <div className="score-card">
          <div className="label">Wellness Score</div>
          <div className="score">{data?.wellness_score ?? "–"}</div>
          <div className="muted small">0 = weak week, 100 = great week</div>
        </div>
      </header>

      <main className="grid">
        <section className="panel">
          <div className="panel-head">
            <h2>Category Breakdown</h2>
            <span className="muted small">Normalized against the past 28 days</span>
          </div>
          {isLoading && <div className="muted">Loading data…</div>}
          {error && <div className="error">Unable to load data. Please start the backend.</div>}
          <div className="pill-row">
            {Object.entries(metrics).map(([label, value]) => (
              <MetricPill key={label} label={label} value={value} />
            ))}
          </div>
        </section>

        <section className="panel">
          <div className="panel-head">
            <h2>Notable Trends</h2>
            <span className="muted small">Anomalies vs month baseline</span>
          </div>
          <AnomalyList anomalies={anomalies} />
        </section>

        <section className="panel full">
          <div className="panel-head">
            <h2>AI Suggestion</h2>
            <span className="muted small">Non-medical, action-focused guidance</span>
          </div>
          <div className="suggestion">
            {suggestion || "No suggestion generated yet. Check backend connectivity."}
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;

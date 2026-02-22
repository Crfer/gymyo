import { FormEvent, useState } from "react";

import { api, ApiError } from "../api/client";
import type { DailyMetricsUpdate, SessionMetrics } from "../api/types";

const USER_ID = 1;

export function MetricsPage(): JSX.Element {
  const [metrics, setMetrics] = useState<SessionMetrics>({
    date: new Date().toISOString().slice(0, 10),
    sleep_hours: 7,
    resting_hr: 55,
    hrv_rmssd: 55,
    soreness: 3,
    motivation: 7,
    rpe_session: 7,
    duration_min: 60,
  });
  const [message, setMessage] = useState("");

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    const payload: DailyMetricsUpdate = { user_id: USER_ID, metrics };
    try {
      const result = await api.updateMetrics(payload);
      setMessage(`${result.status} for ${result.date}`);
    } catch (err) {
      setMessage(err instanceof ApiError ? err.message : "Failed to update metrics");
    }
  };

  return (
    <form className="card grid gap-3 md:grid-cols-2" onSubmit={submit}>
      {Object.entries(metrics).map(([key, value]) => (
        <label className="label" key={key}>
          {key}
          <input
            className="input"
            type={key === "date" ? "date" : "number"}
            step="any"
            value={value}
            onChange={(event) => setMetrics((prev) => ({ ...prev, [key]: key === "date" ? event.target.value : Number(event.target.value) }))}
          />
        </label>
      ))}
      <button className="btn md:col-span-2" type="submit">
        Update Metrics
      </button>
      {message && <p className="md:col-span-2 text-sm text-slate-300">{message}</p>}
    </form>
  );
}

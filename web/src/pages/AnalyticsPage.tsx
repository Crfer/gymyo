import { useEffect, useMemo, useState } from "react";
import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis, Bar, BarChart } from "recharts";

import { api, ApiError } from "../api/client";
import type { AnalyticsResponse } from "../api/types";

const USER_ID = 1;

export function AnalyticsPage(): JSX.Element {
  const [exercise, setExercise] = useState("Squat");
  const [data, setData] = useState<AnalyticsResponse | null>(null);
  const [error, setError] = useState("");

  const load = () => {
    api
      .getAnalytics(USER_ID, exercise)
      .then((payload) => {
        setData(payload);
        setError("");
      })
      .catch((err: unknown) => {
        setError(err instanceof ApiError ? err.message : "Failed to load analytics");
      });
  };

  useEffect(load, []);

  const weeklyData = useMemo(() => {
    if (!data) return [];
    return data.weekly_volume.map((point) => ({
      week: point.week_start,
      muscle: point.muscle,
      volume: point.volume,
    }));
  }, [data]);

  if (error) return <p className="text-red-400">{error}</p>;
  if (!data) return <p>Loading analytics...</p>;

  return (
    <div className="space-y-4">
      <section className="card flex items-end gap-3">
        <label className="label flex-1">
          Exercise for e1RM trend
          <input className="input" value={exercise} onChange={(event) => setExercise(event.target.value)} />
        </label>
        <button className="btn" onClick={load} type="button">
          Refresh
        </button>
      </section>

      <section className="card">
        <h2 className="mb-2 text-lg font-semibold">Weekly Volume by Muscle</h2>
        <div className="h-80">
          <ResponsiveContainer>
            <BarChart data={weeklyData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="week" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="volume" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>

      <section className="card">
        <h2 className="mb-2 text-lg font-semibold">e1RM Trend</h2>
        <div className="h-80">
          <ResponsiveContainer>
            <LineChart data={data.e1rm_trend}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="e1rm" stroke="#22d3ee" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </section>
    </div>
  );
}

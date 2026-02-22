import { useEffect, useState } from "react";

import { api, ApiError } from "../api/client";
import type { DashboardResponse } from "../api/types";

const USER_ID = 1;

export function DashboardPage(): JSX.Element {
  const [data, setData] = useState<DashboardResponse | null>(null);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    api
      .getDashboard(USER_ID)
      .then(setData)
      .catch((err: unknown) => {
        setError(err instanceof ApiError ? err.message : "Failed to load dashboard");
      });
  }, []);

  if (error) {
    return <p className="text-red-400">{error}</p>;
  }

  if (!data) {
    return <p className="text-slate-300">Loading dashboard...</p>;
  }

  return (
    <div className="grid gap-4 md:grid-cols-2">
      <section className="card">
        <h2 className="mb-2 text-lg font-semibold">Next Workout</h2>
        <p className="text-sm text-slate-300">{data.next_workout.target_date}</p>
        <p className="mt-2 text-xl font-bold">{data.next_workout.exercise}</p>
        <p>
          {data.next_workout.sets} sets × {data.next_workout.reps} reps @ {data.next_workout.load_kg} kg
        </p>
      </section>

      <section className="card">
        <h2 className="mb-2 text-lg font-semibold">Latest Metrics</h2>
        <ul className="space-y-1 text-sm text-slate-200">
          <li>Date: {data.latest_metrics.date}</li>
          <li>Sleep: {data.latest_metrics.sleep_hours}h</li>
          <li>Resting HR: {data.latest_metrics.resting_hr}</li>
          <li>HRV: {data.latest_metrics.hrv_rmssd}</li>
          <li>Soreness: {data.latest_metrics.soreness}/10</li>
        </ul>
      </section>

      <section className="card md:col-span-2">
        <h2 className="mb-2 text-lg font-semibold">Recent Sessions</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="text-slate-400">
              <tr>
                <th>Date</th>
                <th>Exercises</th>
                <th>Tonnage</th>
                <th>Avg RIR</th>
              </tr>
            </thead>
            <tbody>
              {data.recent_sessions.map((session) => (
                <tr className="border-t border-slate-800" key={session.date}>
                  <td className="py-2">{session.date}</td>
                  <td>{session.exercise_count}</td>
                  <td>{session.tonnage}</td>
                  <td>{session.avg_rir}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

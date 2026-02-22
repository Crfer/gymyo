import { FormEvent, useState } from "react";

import { api, ApiError } from "../api/client";
import type { ExerciseLog, SessionInput, SessionMetrics } from "../api/types";

const USER_ID = 1;

function defaultMetrics(): SessionMetrics {
  const today = new Date().toISOString().slice(0, 10);
  return {
    date: today,
    sleep_hours: 7,
    resting_hr: 55,
    hrv_rmssd: 55,
    soreness: 3,
    motivation: 7,
    rpe_session: 7,
    duration_min: 60,
  };
}

export function LogSessionPage(): JSX.Element {
  const [metrics, setMetrics] = useState<SessionMetrics>(defaultMetrics());
  const [exercises, setExercises] = useState<ExerciseLog[]>([
    { exercise: "Squat", sets: 4, reps: 5, load_kg: 100, rir: 2 },
  ]);
  const [message, setMessage] = useState<string>("");

  const updateExercise = (index: number, patch: Partial<ExerciseLog>) => {
    setExercises((prev) => prev.map((row, i) => (i === index ? { ...row, ...patch } : row)));
  };

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    const payload: SessionInput = { user_id: USER_ID, metrics, exercises };
    try {
      const response = await api.logSession(payload);
      setMessage(`Session logged with ID ${response.session_id}`);
    } catch (err) {
      setMessage(err instanceof ApiError ? err.message : "Failed to log session");
    }
  };

  return (
    <form className="space-y-4" onSubmit={submit}>
      <section className="card grid gap-3 md:grid-cols-3">
        <h2 className="md:col-span-3 text-lg font-semibold">Session Metrics</h2>
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
      </section>

      <section className="card space-y-3">
        <h2 className="text-lg font-semibold">Exercises</h2>
        {exercises.map((exercise, index) => (
          <div className="grid gap-2 md:grid-cols-5" key={`${exercise.exercise}-${index}`}>
            <input className="input" value={exercise.exercise} onChange={(event) => updateExercise(index, { exercise: event.target.value })} />
            <input className="input" type="number" value={exercise.sets} onChange={(event) => updateExercise(index, { sets: Number(event.target.value) })} />
            <input className="input" type="number" value={exercise.reps} onChange={(event) => updateExercise(index, { reps: Number(event.target.value) })} />
            <input className="input" type="number" step="0.5" value={exercise.load_kg} onChange={(event) => updateExercise(index, { load_kg: Number(event.target.value) })} />
            <input className="input" type="number" step="0.5" value={exercise.rir} onChange={(event) => updateExercise(index, { rir: Number(event.target.value) })} />
          </div>
        ))}
        <button className="btn" type="button" onClick={() => setExercises((prev) => [...prev, { exercise: "", sets: 3, reps: 8, load_kg: 40, rir: 2 }])}>
          Add Exercise
        </button>
      </section>

      <button className="btn" type="submit">
        Submit Session
      </button>
      {message && <p className="text-sm text-slate-300">{message}</p>}
    </form>
  );
}

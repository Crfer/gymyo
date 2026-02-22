import { FormEvent, useEffect, useState } from "react";

import { api, ApiError } from "../api/client";
import type { ProfileUpdate } from "../api/types";

const initial: ProfileUpdate = {
  age: 30,
  bodyweight_kg: 80,
  training_age_years: 2,
  goal: "hypertrophy",
  mrv_baseline_sets: 14,
};

export function ProfilePage(): JSX.Element {
  const [profile, setProfile] = useState<ProfileUpdate>(initial);
  const [message, setMessage] = useState("");

  useEffect(() => {
    api
      .getProfile()
      .then((payload) => {
        setProfile({
          age: payload.age,
          bodyweight_kg: payload.bodyweight_kg,
          training_age_years: payload.training_age_years,
          goal: payload.goal,
          mrv_baseline_sets: payload.mrv_baseline_sets,
        });
      })
      .catch((err: unknown) => setMessage(err instanceof ApiError ? err.message : "Failed to load profile"));
  }, []);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    try {
      await api.updateProfile(profile);
      setMessage("Profile saved");
    } catch (err) {
      setMessage(err instanceof ApiError ? err.message : "Failed to save profile");
    }
  };

  return (
    <form className="card grid gap-3 md:grid-cols-2" onSubmit={submit}>
      <label className="label">
        Age
        <input className="input" type="number" value={profile.age} onChange={(event) => setProfile((prev) => ({ ...prev, age: Number(event.target.value) }))} />
      </label>
      <label className="label">
        Bodyweight (kg)
        <input className="input" type="number" step="0.1" value={profile.bodyweight_kg} onChange={(event) => setProfile((prev) => ({ ...prev, bodyweight_kg: Number(event.target.value) }))} />
      </label>
      <label className="label">
        Training age (years)
        <input className="input" type="number" step="0.1" value={profile.training_age_years} onChange={(event) => setProfile((prev) => ({ ...prev, training_age_years: Number(event.target.value) }))} />
      </label>
      <label className="label">
        Goal
        <input className="input" value={profile.goal} onChange={(event) => setProfile((prev) => ({ ...prev, goal: event.target.value }))} />
      </label>
      <label className="label md:col-span-2">
        MRV baseline sets
        <input className="input" type="number" value={profile.mrv_baseline_sets} onChange={(event) => setProfile((prev) => ({ ...prev, mrv_baseline_sets: Number(event.target.value) }))} />
      </label>
      <button className="btn md:col-span-2" type="submit">
        Save Profile
      </button>
      {message && <p className="md:col-span-2 text-sm text-slate-300">{message}</p>}
    </form>
  );
}

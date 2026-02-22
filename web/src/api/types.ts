export type UserProfile = {
  user_id: number;
  age: number;
  bodyweight_kg: number;
  training_age_years: number;
  goal: string;
  mrv_baseline_sets: number;
};

export type ProfileUpdate = Omit<UserProfile, "user_id">;

export type ExerciseLog = {
  exercise: string;
  sets: number;
  reps: number;
  load_kg: number;
  rir: number;
};

export type SessionMetrics = {
  date: string;
  sleep_hours: number;
  resting_hr: number;
  hrv_rmssd: number;
  soreness: number;
  motivation: number;
  rpe_session: number;
  duration_min: number;
};

export type SessionInput = {
  user_id: number;
  metrics: SessionMetrics;
  exercises: ExerciseLog[];
};

export type DailyMetricsUpdate = {
  user_id: number;
  metrics: SessionMetrics;
};

export type TrainingPrescription = {
  target_date: string;
  exercise: string;
  sets: number;
  reps: number;
  load_kg: number;
  deload: boolean;
  rationale: Record<string, string | number>;
};

export type SessionSummary = {
  date: string;
  exercise_count: number;
  tonnage: number;
  avg_rir: number;
};

export type DashboardResponse = {
  next_workout: TrainingPrescription;
  latest_metrics: SessionMetrics;
  recent_sessions: SessionSummary[];
};

export type WeeklyVolumePoint = {
  week_start: string;
  muscle: string;
  volume: number;
};

export type E1RMPoint = {
  date: string;
  exercise: string;
  e1rm: number;
};

export type AnalyticsResponse = {
  sessions: number;
  fatigue_mean: number;
  stimulus_mean: number;
  readiness_mean: number;
  weekly_volume: WeeklyVolumePoint[];
  e1rm_trend: E1RMPoint[];
};

import type {
  AnalyticsResponse,
  DailyMetricsUpdate,
  DashboardResponse,
  ProfileUpdate,
  SessionInput,
  TrainingPrescription,
  UserProfile,
} from "./types";

class ApiError extends Error {
  readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`/api${path}`, {
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
    ...init,
  });

  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = (await response.json()) as { detail?: string };
      detail = body.detail ?? detail;
    } catch {
      detail = response.statusText;
    }
    throw new ApiError(response.status, detail);
  }

  return (await response.json()) as T;
}

export const api = {
  getProfile: () => request<UserProfile>("/profile"),
  updateProfile: (payload: ProfileUpdate) => request<UserProfile>("/profile", { method: "PUT", body: JSON.stringify(payload) }),
  logSession: (payload: SessionInput) => request<{ session_id: number }>("/log-session", { method: "POST", body: JSON.stringify(payload) }),
  updateMetrics: (payload: DailyMetricsUpdate) => request<{ status: string; date: string }>("/update-metrics", { method: "POST", body: JSON.stringify(payload) }),
  getNextWorkout: (userId: number) => request<TrainingPrescription>(`/next-workout?user_id=${userId}`),
  getAnalytics: (userId: number, exercise: string) => request<AnalyticsResponse>(`/analytics?user_id=${userId}&exercise=${encodeURIComponent(exercise)}`),
  getDashboard: (userId: number) => request<DashboardResponse>(`/dashboard?user_id=${userId}`),
};

export { ApiError };

import { Navigate, Route, Routes } from "react-router-dom";

import { Layout } from "./components/Layout";
import { AnalyticsPage } from "./pages/AnalyticsPage";
import { DashboardPage } from "./pages/DashboardPage";
import { LogSessionPage } from "./pages/LogSessionPage";
import { MetricsPage } from "./pages/MetricsPage";
import { ProfilePage } from "./pages/ProfilePage";

export default function App(): JSX.Element {
  return (
    <Routes>
      <Route element={<Layout />} path="/">
        <Route element={<DashboardPage />} index />
        <Route element={<LogSessionPage />} path="log-session" />
        <Route element={<MetricsPage />} path="metrics" />
        <Route element={<AnalyticsPage />} path="analytics" />
        <Route element={<ProfilePage />} path="profile" />
        <Route element={<Navigate to="/" replace />} path="*" />
      </Route>
    </Routes>
  );
}

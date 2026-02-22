import { Link, Outlet, useLocation } from "react-router-dom";

const links = [
  ["/", "Dashboard"],
  ["/log-session", "Log Session"],
  ["/metrics", "Metrics"],
  ["/analytics", "Analytics"],
  ["/profile", "Profile"],
] as const;

export function Layout(): JSX.Element {
  const location = useLocation();

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <header className="border-b border-slate-800 bg-slate-900 px-6 py-4">
        <h1 className="text-xl font-bold">Gymyo Adaptive Training</h1>
      </header>
      <nav className="border-b border-slate-800 px-6 py-3">
        <ul className="flex flex-wrap gap-3">
          {links.map(([href, label]) => (
            <li key={href}>
              <Link
                className={`rounded px-3 py-1 text-sm ${
                  location.pathname === href ? "bg-blue-500 text-white" : "bg-slate-800 text-slate-300"
                }`}
                to={href}
              >
                {label}
              </Link>
            </li>
          ))}
        </ul>
      </nav>
      <main className="mx-auto max-w-6xl p-6">
        <Outlet />
      </main>
    </div>
  );
}

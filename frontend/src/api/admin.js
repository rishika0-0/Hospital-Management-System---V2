import http from "./http";

export function getAdminDashboard() {
  return http.get("/api/admin/dashboard");
}

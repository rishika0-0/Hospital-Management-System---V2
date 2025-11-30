import http from "./http";

export function loginApi(email, password) {
  return http.post("/api/auth/login", { email, password });
}

export function registerApi(payload) {
  return http.post("/api/auth/register", payload);
}

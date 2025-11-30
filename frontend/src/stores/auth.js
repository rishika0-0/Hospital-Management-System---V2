import { reactive, computed } from "vue";

const state = reactive({
  user: localStorage.getItem("user")
    ? JSON.parse(localStorage.getItem("user"))
    : null,
  token: localStorage.getItem("access_token") || null,
});

export function useAuth() {
  const isAuthenticated = computed(() => !!state.token);
  const role = computed(() => state.user?.role || null);

  function login(user, token) {
    state.user = user;
    state.token = token;
    localStorage.setItem("user", JSON.stringify(user));
    localStorage.setItem("access_token", token);
  }

  function logout() {
    state.user = null;
    state.token = null;
    localStorage.removeItem("user");
    localStorage.removeItem("access_token");
  }

  return {
    state,
    isAuthenticated,
    role,
    login,
    logout,
  };
}

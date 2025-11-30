<template>
  <div class="auth-wrapper d-flex align-items-center justify-content-center">
    <div class="auth-card shadow-lg p-4 rounded-4 bg-white">
      <h4 class="text-center fw-bold mb-1 text-primary">
        Hospital Management System
      </h4>
      <p class="text-center text-muted mb-4">Sign in</p>

      <div v-if="errorText" class="alert alert-danger py-2">
        {{ errorText }}
      </div>

      <form @submit.prevent="handleLogin">
        <div class="mb-3">
          <label class="form-label">Email</label>
          <input
            v-model="emailInput"
            type="email"
            class="form-control"
            placeholder="you@example.com"
            required
          />
        </div>

        <div class="mb-2">
          <label class="form-label">Password</label>
          <input
            v-model="passwordInput"
            type="password"
            class="form-control"
            placeholder="••••••••"
            required
          />
        </div>

        <div class="d-flex justify-content-between align-items-center mb-3">
          <div class="form-check">
            <input
              class="form-check-input"
              type="checkbox"
              id="rememberCheck"
            />
            <label class="form-check-label small" for="rememberCheck">
              Keep me signed in
            </label>
          </div>
        </div>

        <button type="submit" class="btn btn-primary w-100" :disabled="loading">
          <span v-if="!loading">Login</span>
          <span v-else class="spinner-border spinner-border-sm"></span>
        </button>
      </form>

      <p class="text-center small mt-3 mb-0">
        New patient?
        <a href="javascript:void(0)" @click="goRegister">Create an account</a>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import api from "../api/http";

const router = useRouter();

const emailInput = ref("");
const passwordInput = ref("");
const loading = ref(false);
const errorText = ref("");

const handleLogin = async () => {
  errorText.value = "";
  loading.value = true;
  try {
    const res = await api.post("/auth/login", {
      email: emailInput.value,
      password: passwordInput.value,
    });

    localStorage.setItem("authToken", res.data.access_token);
    localStorage.setItem("userRole", res.data.user.role);

    const target = res.data.redirect || "/";
    router.push(target);
  } catch (err) {
    errorText.value =
      err?.response?.data?.msg || "Unable to login. Please check credentials.";
  } finally {
    loading.value = false;
  }
};

const goRegister = () => {
  router.push("/register");
};
</script>

<style scoped>
.auth-wrapper {
  min-height: 100vh;
}
.auth-card {
  width: 100%;
  max-width: 420px;
}
</style>

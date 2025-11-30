<template>
  <div class="auth-wrapper d-flex align-items-center justify-content-center">
    <div class="auth-card shadow-lg p-4 rounded-4 bg-white">
      <h4 class="text-center fw-bold mb-1 text-primary">
        Hospital Management System
      </h4>
      <p class="text-center text-muted mb-4">Create your account</p>

      <!-- Alerts -->
      <div v-if="errorText" class="alert alert-danger py-2">
        {{ errorText }}
      </div>
      <div v-if="successText" class="alert alert-success py-2">
        {{ successText }}
      </div>

      <form @submit.prevent="handleRegister">
        <div class="mb-3">
          <label class="form-label fw-semibold text-primary">Full Name</label>
          <input
            v-model="nameInput"
            type="text"
            class="form-control input-blue"
            placeholder="Your name"
            required
          />
        </div>

        <div class="mb-3">
          <label class="form-label fw-semibold text-primary">Email</label>
          <input
            v-model="emailInput"
            type="email"
            class="form-control input-blue"
            placeholder="you@example.com"
            required
          />
        </div>

        <div class="mb-3">
          <label class="form-label fw-semibold text-primary">Password</label>
          <input
            v-model="passwordInput"
            type="password"
            class="form-control input-blue"
            placeholder="Choose password"
            required
          />
        </div>

        <button type="submit" class="btn btn-blue w-100" :disabled="loading">
          <span v-if="!loading">Create Account</span>
          <span v-else class="spinner-border spinner-border-sm"></span>
        </button>
      </form>

      <p class="text-center small mt-3 mb-0 text-dark">
        Already registered?
        <a
          href="javascript:void(0)"
          class="text-primary fw-semibold"
          @click="goLogin"
          >Login</a
        >
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import api from "../api/http";

const router = useRouter();

const nameInput = ref("");
const emailInput = ref("");
const passwordInput = ref("");

const loading = ref(false);
const errorText = ref("");
const successText = ref("");

const handleRegister = async () => {
  loading.value = true;
  errorText.value = "";
  successText.value = "";

  try {
    await api.post("/auth/register", {
      username: emailInput.value,
      email: emailInput.value,
      password: passwordInput.value,
      name: nameInput.value,
    });

    successText.value = "Registration successful! Redirecting...";
    setTimeout(() => router.push("/login"), 1200);
  } catch (err) {
    errorText.value =
      err?.response?.data?.msg || "Failed to register. Try again.";
  } finally {
    loading.value = false;
  }
};

const goLogin = () => router.push("/login");
</script>

<style scoped>
.auth-wrapper {
  min-height: 100vh;
}

.auth-card {
  width: 100%;
  max-width: 450px;
}

.input-blue {
  border: 1.7px solid #c7d2fe;
  transition: 0.3s;
  border-radius: 10px;
}

.input-blue:focus {
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.25);
}

.btn-blue {
  background: linear-gradient(135deg, #2563eb, #0ea5e9);
  border: none;
  color: white;
  font-weight: 600;
  padding: 10px;
  border-radius: 999px;
  transition: 0.25s;
}
.btn-blue:hover {
  opacity: 0.9;
  transform: scale(1.02);
}
</style>

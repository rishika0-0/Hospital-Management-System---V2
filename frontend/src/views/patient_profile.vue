<template>
  <div class="container mt-4" v-if="!loading">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h3>My Profile</h3>
      <button class="btn btn-outline-secondary btn-sm" @click="goBack">
        Back to Dashboard
      </button>
    </div>

    <div v-if="errorMsg" class="alert alert-danger">{{ errorMsg }}</div>
    <div v-if="successMsg" class="alert alert-success">{{ successMsg }}</div>

    <div class="card">
      <div class="card-body">
        <form @submit.prevent="saveProfile">
          <div class="row">
            <div class="col-md-6 mb-3">
              <label class="form-label">Name</label>
              <input v-model="form.name" type="text" class="form-control" />
            </div>

            <div class="col-md-6 mb-3">
              <label class="form-label">Email</label>
              <input v-model="form.email" type="email" class="form-control" />
            </div>

            <div class="col-md-6 mb-3">
              <label class="form-label">Contact</label>
              <input v-model="form.contact" type="text" class="form-control" />
            </div>

            <div class="col-md-6 mb-3">
              <label class="form-label">Address</label>
              <input v-model="form.address" type="text" class="form-control" />
            </div>

            <div class="col-md-6 mb-3">
              <label class="form-label">New Password</label>
              <input
                v-model="form.password"
                type="password"
                class="form-control"
                placeholder="Leave blank to keep current"
              />
            </div>
          </div>

          <button type="submit" class="btn btn-primary">Save Changes</button>
        </form>
      </div>
    </div>
  </div>

  <div
    v-else
    class="d-flex justify-content-center align-items-center"
    style="min-height: 60vh"
  >
    <div class="spinner-border" role="status">
      <span class="visually-hidden">Loading...</span>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue";
import { useRouter } from "vue-router";
import api from "../api/http";

const router = useRouter();

const loading = ref(true);
const errorMsg = ref("");
const successMsg = ref("");

const form = reactive({
  name: "",
  email: "",
  contact: "",
  address: "",
  password: "",
});

const loadProfile = async () => {
  loading.value = true;
  errorMsg.value = "";
  try {
    const res = await api.get("/patient/profile");
    form.name = res.data.name || "";
    form.email = res.data.email || "";
    form.contact = res.data.contact || "";
    form.address = res.data.address || "";
    form.password = "";
  } catch (err) {
    console.error(err);
    errorMsg.value =
      err?.response?.data?.msg || "Failed to load profile details.";
  } finally {
    loading.value = false;
  }
};

onMounted(loadProfile);

const saveProfile = async () => {
  errorMsg.value = "";
  successMsg.value = "";
  try {
    await api.put("/patient/profile", {
      name: form.name,
      email: form.email,
      contact: form.contact,
      address: form.address,
      password: form.password || undefined,
    });
    successMsg.value = "Profile updated successfully.";
    form.password = "";
  } catch (err) {
    console.error(err);
    errorMsg.value = err?.response?.data?.msg || "Failed to update profile.";
  }
};

const goBack = () => {
  router.push("/patient/dashboard");
};
</script>

<style scoped>
.card {
  border-radius: 14px;
  box-shadow: 0 8px 20px rgba(15, 23, 42, 0.1);
}
</style>

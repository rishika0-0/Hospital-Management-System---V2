<template>
  <div class="container mt-4" v-if="!loading">
    <h3>Manage Availability</h3>

    <div v-if="errorMsg" class="alert alert-danger mt-3">
      {{ errorMsg }}
    </div>

    <div class="card mt-3">
      <div class="card-body">
        <div class="mb-3">
          <label class="form-label">Current Availability</label>
          <p v-if="currentAvailability" class="fw-semibold">
            {{ currentAvailability }}
          </p>
          <p v-else class="text-muted fst-italic">Not configured yet.</p>
        </div>

        <form @submit.prevent="saveAvailability">
          <div class="mb-3">
            <label class="form-label">New Availability</label>
            <input
              v-model="availabilityInput"
              type="text"
              class="form-control"
              placeholder="Example: Mon-Fri: 09:00-12:00"
            />
          </div>

          <div class="d-flex gap-2">
            <button type="submit" class="btn btn-primary">
              Save &amp; Regenerate Slots
            </button>
            <button type="button" class="btn btn-secondary" @click="goBack">
              Back to Dashboard
            </button>
          </div>
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
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import api from "../api/http";

const router = useRouter();

const loading = ref(true);
const errorMsg = ref("");

const currentAvailability = ref("");
const availabilityInput = ref("");

const fetchAvailability = async () => {
  loading.value = true;
  errorMsg.value = "";
  try {
    const res = await api.get("/doctor/availability");
    currentAvailability.value = res.data.availability || "";
    availabilityInput.value = res.data.availability || "";
  } catch (err) {
    console.error(err);
    errorMsg.value = err?.response?.data?.msg || "Failed to load availability.";
  } finally {
    loading.value = false;
  }
};

onMounted(fetchAvailability);

const saveAvailability = async () => {
  if (!availabilityInput.value.trim()) {
    alert("Please enter an availability string.");
    return;
  }
  try {
    await api.put("/doctor/availability", {
      availability: availabilityInput.value.trim(),
    });
    alert("Availability updated. Slots regenerated for next 7 days.");
    await fetchAvailability();
  } catch (err) {
    console.error(err);
    alert(err?.response?.data?.msg || "Failed to update availability.");
  }
};

const goBack = () => {
  router.push("/doctor/dashboard");
};
</script>

<style scoped>
.card {
  border-radius: 14px;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.12);
}
</style>

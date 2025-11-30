<template>
  <div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <div>
        <h3>Book Appointment</h3>
        <p class="mb-0 text-muted">
          Doctor: <strong>{{ doctorName || "Loading..." }}</strong>
        </p>
      </div>
      <button class="btn btn-outline-secondary btn-sm" @click="goBack">
        Back to Doctors
      </button>
    </div>

    <div v-if="errorMsg" class="alert alert-danger">{{ errorMsg }}</div>

    <div v-if="loading" class="text-center mt-4">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <div v-else>
      <div class="card">
        <div class="card-header">Available Slots (Next 7 Days)</div>
        <div class="card-body table-responsive">
          <table class="table table-striped align-middle">
            <thead>
              <tr>
                <th>Date</th>
                <th>Day</th>
                <th>Time</th>
                <th>Status</th>
                <th>Book</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="s in slots" :key="s.slot_id">
                <td>{{ s.date }}</td>
                <td>{{ s.weekday }}</td>
                <td>{{ s.start_time }} - {{ s.end_time }}</td>
                <td>
                  <span
                    class="badge"
                    :class="s.is_booked ? 'bg-danger' : 'bg-success'"
                  >
                    {{ s.is_booked ? "Booked" : "Available" }}
                  </span>
                </td>
                <td>
                  <button
                    class="btn btn-sm btn-primary"
                    :disabled="s.is_booked"
                    @click="bookSlot(s.slot_id)"
                  >
                    Book
                  </button>
                </td>
              </tr>
              <tr v-if="slots.length === 0">
                <td colspan="5" class="text-center text-muted">
                  No slots available for this doctor.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <p class="text-muted mt-2" v-if="!errorMsg">
        Note: Only slots marked as
        <span class="badge bg-success">Available</span> can be booked.
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import api from "../api/http";

const route = useRoute();
const router = useRouter();

const doctorId = route.params.id;

const doctorName = ref("");
const slots = ref([]);
const loading = ref(true);
const errorMsg = ref("");

const loadSlots = async () => {
  loading.value = true;
  errorMsg.value = "";
  try {
    const res = await api.get(`/patient/doctors/${doctorId}/slots`);
    doctorName.value = res.data.doctor_name || "";
    slots.value = res.data.slots || [];
  } catch (err) {
    console.error(err);
    errorMsg.value =
      err?.response?.data?.msg || "Failed to load slots for this doctor.";
  } finally {
    loading.value = false;
  }
};

onMounted(loadSlots);

const bookSlot = async (slotId) => {
  const ok = window.confirm("Confirm booking this slot?");
  if (!ok) return;

  try {
    await api.post(`/patient/doctors/${doctorId}/book`, { slot_id: slotId });
    alert("Appointment booked successfully.");
    router.push("/patient/dashboard");
  } catch (err) {
    console.error(err);
    alert(err?.response?.data?.msg || "Failed to book appointment.");
  }
};

const goBack = () => {
  router.push("/patient/doctors");
};
</script>

<style scoped>
.card {
  border-radius: 14px;
  box-shadow: 0 8px 20px rgba(15, 23, 42, 0.1);
}
</style>

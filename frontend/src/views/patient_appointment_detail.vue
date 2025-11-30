<template>
  <div class="container mt-4" v-if="appointment">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h3>Appointment Details</h3>
      <button class="btn btn-secondary btn-sm" @click="goBack">
        Back to Dashboard
      </button>
    </div>

    <div class="row">
      <!-- Basic info -->
      <div class="col-md-4 mb-3">
        <div class="card p-3">
          <h5 class="mb-2">Appointment #{{ appointment.id }}</h5>
          <p class="mb-1"><strong>Date:</strong> {{ appointment.date }}</p>
          <p class="mb-1">
            <strong>Time:</strong>
            {{ appointment.start_time }} - {{ appointment.end_time }}
          </p>
          <p class="mb-1">
            <strong>Doctor:</strong> {{ appointment.doctor_name || "—" }}
          </p>
          <p class="mb-0">
            <strong>Status:</strong>
            <span :class="['badge', badgeClass(appointment.status)]">
              {{ appointment.status }}
            </span>
          </p>
        </div>
      </div>

      <!-- Treatment info -->
      <div class="col-md-8 mb-3">
        <div class="card p-3">
          <h5 class="mb-3">Diagnosis &amp; Treatment</h5>

          <div class="mb-2">
            <strong>Diagnosis:</strong>
            <p class="mb-1">
              {{ appointment.diagnosis || "No diagnosis recorded yet." }}
            </p>
          </div>

          <div class="mb-2">
            <strong>Prescription:</strong>
            <p class="mb-1">
              {{ appointment.prescription || "No prescription recorded yet." }}
            </p>
          </div>

          <div class="mb-2">
            <strong>Notes:</strong>
            <p class="mb-0">
              {{ appointment.notes || "No additional notes." }}
            </p>
          </div>

          <div class="mt-3">
            <button
              v-if="appointment.status === 'Booked'"
              class="btn btn-outline-primary btn-sm me-2"
              @click="goReschedule"
            >
              Reschedule
            </button>
            <button
              v-if="appointment.status === 'Booked'"
              class="btn btn-outline-danger btn-sm"
              @click="cancel"
            >
              Cancel Appointment
            </button>
          </div>
        </div>
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
import { useRoute, useRouter } from "vue-router";
import api from "../api/http";

const route = useRoute();
const router = useRouter();
const apptId = route.params.id;

const appointment = ref(null);

const loadAppointment = async () => {
  const res = await api.get(`/patient/appointments/${apptId}`);
  appointment.value = res.data;
};

onMounted(loadAppointment);

const badgeClass = (status) => {
  if (status === "Completed") return "bg-success";
  if (status === "Cancelled") return "bg-danger";
  return "bg-secondary";
};

const goBack = () => {
  router.push("/patient/dashboard");
};

const goReschedule = () => {
  router.push(`/patient/appointments/${apptId}/reschedule`);
};

const cancel = async () => {
  const ok = window.confirm("Cancel this appointment?");
  if (!ok) return;
  try {
    await api.patch(`/patient/appointments/${apptId}/cancel`);
    alert("Appointment cancelled.");
    router.push("/patient/dashboard");
  } catch (err) {
    console.error(err);
    alert(err?.response?.data?.msg || "Failed to cancel appointment.");
  }
};
</script>

<style scoped>
.card {
  border-radius: 14px;
  box-shadow: 0 8px 20px rgba(15, 23, 42, 0.1);
}
</style>

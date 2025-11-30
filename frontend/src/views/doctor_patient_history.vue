<template>
  <div class="container mt-4" v-if="!loading">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h3>Patient History</h3>
      <button class="btn btn-secondary btn-sm" @click="goBack">
        Back to Dashboard
      </button>
    </div>

    <div v-if="errorMsg" class="alert alert-danger">
      {{ errorMsg }}
    </div>

    <div v-if="patient">
      <!-- Patient info -->
      <div class="card mb-3">
        <div class="card-body">
          <h5 class="card-title mb-1">{{ patient.name }}</h5>
          <p class="mb-1"><strong>ID:</strong> {{ patient.id }}</p>
          <p class="mb-1">
            <strong>Contact:</strong> {{ patient.contact || "—" }}
          </p>
          <p class="mb-0">
            <strong>Status:</strong>
            <span
              :class="['badge', patient.status ? 'bg-success' : 'bg-secondary']"
            >
              {{ patient.status ? "Active" : "Inactive" }}
            </span>
          </p>
        </div>
      </div>

      <!-- Appointments -->
      <div class="card">
        <div class="card-header">Appointment & Treatment History</div>
        <div class="card-body table-responsive">
          <table class="table table-striped align-middle">
            <thead>
              <tr>
                <th>Date</th>
                <th>Time</th>
                <th>Status</th>
                <th>Diagnosis</th>
                <th>Prescription</th>
                <th>Notes</th>
                <th>Open</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="a in history" :key="a.id">
                <td>{{ a.date }}</td>
                <td>{{ a.start_time }} - {{ a.end_time }}</td>
                <td>
                  <span :class="['badge', badgeClass(a.status)]">
                    {{ a.status }}
                  </span>
                </td>
                <td>{{ a.diagnosis || "—" }}</td>
                <td>{{ a.prescription || "—" }}</td>
                <td>{{ a.notes || "—" }}</td>
                <td>
                  <button
                    class="btn btn-sm btn-outline-primary"
                    @click="openAppointment(a.id)"
                  >
                    View / Edit
                  </button>
                </td>
              </tr>
              <tr v-if="history.length === 0">
                <td colspan="7" class="text-center text-muted">
                  No appointment history for this patient.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div v-else class="alert alert-warning">Patient not found.</div>
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

const patientId = route.params.id;

const loading = ref(true);
const errorMsg = ref("");

const patient = ref(null);
const history = ref([]);

const fetchHistory = async () => {
  loading.value = true;
  errorMsg.value = "";
  try {
    const res = await api.get(`/doctor/patients/${patientId}/history`);
    patient.value = res.data.patient;
    history.value = res.data.appointments || [];
  } catch (err) {
    console.error(err);
    errorMsg.value =
      err?.response?.data?.msg || "Failed to load patient history.";
  } finally {
    loading.value = false;
  }
};

onMounted(fetchHistory);

const badgeClass = (status) => {
  if (status === "Completed") return "bg-success";
  if (status === "Cancelled") return "bg-danger";
  return "bg-secondary";
};

const openAppointment = (apptId) => {
  router.push(`/doctor/appointment/${apptId}`);
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

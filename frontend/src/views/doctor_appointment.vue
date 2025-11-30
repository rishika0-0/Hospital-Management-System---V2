<template>
  <div class="container mt-4" v-if="appointment">
    <h3>Appointment #{{ appointment.id }}</h3>

    <div class="row mt-3">
      <!-- Left: basic info -->
      <div class="col-md-4 mb-3">
        <div class="card p-3">
          <h5 class="mb-2">Details</h5>
          <p><strong>Date:</strong> {{ appointment.date }}</p>
          <p>
            <strong>Time:</strong>
            {{ appointment.start_time }} - {{ appointment.end_time }}
          </p>
          <p><strong>Patient:</strong> {{ appointment.patient_name }}</p>
          <p>
            <strong>Status:</strong>
            <span :class="['badge', statusBadge(appointment.status)]">
              {{ appointment.status }}
            </span>
          </p>

          <div class="mt-2">
            <label class="form-label">Update Status</label>
            <div class="btn-group btn-group-sm d-flex">
              <button
                class="btn"
                :class="
                  appointment.status === 'Booked'
                    ? 'btn-primary'
                    : 'btn-outline-primary'
                "
                @click="updateStatus('Booked')"
              >
                Booked
              </button>
              <button
                class="btn"
                :class="
                  appointment.status === 'Completed'
                    ? 'btn-success'
                    : 'btn-outline-success'
                "
                @click="updateStatus('Completed')"
              >
                Completed
              </button>
              <button
                class="btn"
                :class="
                  appointment.status === 'Cancelled'
                    ? 'btn-danger'
                    : 'btn-outline-danger'
                "
                @click="updateStatus('Cancelled')"
              >
                Cancelled
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- diagnosis tab -->
      <div class="col-md-8 mb-3">
        <div class="card p-3">
          <h5 class="mb-3">Diagnosis &amp; Treatment</h5>
          <form @submit.prevent="saveTreatment">
            <div class="mb-3">
              <label class="form-label">Diagnosis</label>
              <textarea
                v-model="form.diagnosis"
                rows="2"
                class="form-control"
              ></textarea>
            </div>

            <div class="mb-3">
              <label class="form-label">Prescription</label>
              <textarea
                v-model="form.prescription"
                rows="2"
                class="form-control"
              ></textarea>
            </div>

            <div class="mb-3">
              <label class="form-label">Notes</label>
              <textarea
                v-model="form.notes"
                rows="3"
                class="form-control"
              ></textarea>
            </div>

            <button class="btn btn-primary" type="submit">
              Save Treatment
            </button>
            <button
              type="button"
              class="btn btn-secondary ms-2"
              @click="goBack"
            >
              Back to Dashboard
            </button>
          </form>
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
const form = ref({
  diagnosis: "",
  prescription: "",
  notes: "",
});

const statusBadge = (status) => {
  if (status === "Completed") return "bg-success";
  if (status === "Cancelled") return "bg-danger";
  return "bg-secondary";
};

const loadAppointment = async () => {
  const res = await api.get(`/doctor/appointments/${apptId}`);
  appointment.value = res.data;
  if (res.data.treatment) {
    form.value = {
      diagnosis: res.data.treatment.diagnosis || "",
      prescription: res.data.treatment.prescription || "",
      notes: res.data.treatment.notes || "",
    };
  }
};

onMounted(loadAppointment);

const updateStatus = async (newStatus) => {
  try {
    await api.patch(`/doctor/appointments/${apptId}`, { status: newStatus });
    appointment.value.status = newStatus;
  } catch (err) {
    console.error(err);
    alert(err?.response?.data?.msg || "Failed to update status");
  }
};

const saveTreatment = async () => {
  try {
    await api.patch(`/doctor/appointments/${apptId}`, {
      diagnosis: form.value.diagnosis,
      prescription: form.value.prescription,
      notes: form.value.notes,
    });
    alert("Treatment updated");
  } catch (err) {
    console.error(err);
    alert(err?.response?.data?.msg || "Failed to save treatment");
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

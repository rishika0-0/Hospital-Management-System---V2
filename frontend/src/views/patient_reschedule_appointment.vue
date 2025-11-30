<template>
  <div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h3>Reschedule Appointment</h3>
      <button class="btn btn-secondary btn-sm" @click="goBack">
        Back to Dashboard
      </button>
    </div>

    <div v-if="errorMsg" class="alert alert-danger">{{ errorMsg }}</div>

    <div v-if="loading" class="text-center mt-4">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <div v-else>
      <div class="card mb-3" v-if="doctorName">
        <div class="card-body">
          <p class="mb-1"><strong>Doctor:</strong> {{ doctorName }}</p>
          <p class="mb-1">
            <strong>Current Date:</strong> {{ currentAppointment?.date }}
          </p>
          <p class="mb-0">
            <strong>Current Time:</strong>
            {{ currentAppointment?.start_time }} -
            {{ currentAppointment?.end_time }}
          </p>
        </div>
      </div>

      <div class="card">
        <div class="card-header">Choose a new slot</div>
        <div class="card-body table-responsive">
          <table class="table table-striped align-middle">
            <thead>
              <tr>
                <th>Date</th>
                <th>Day</th>
                <th>Time</th>
                <th>Status</th>
                <th>Reschedule</th>
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
                    @click="chooseSlot(s.slot_id)"
                  >
                    Choose
                  </button>
                </td>
              </tr>
              <tr v-if="slots.length === 0">
                <td colspan="5" class="text-center text-muted">
                  No slots available to reschedule.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <p class="mt-2 text-muted" v-if="!errorMsg">
        Note: Only slots marked as
        <span class="badge bg-success">Available</span> can be selected.
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
const apptId = route.params.id;

const loading = ref(true);
const errorMsg = ref("");
const doctorId = ref(null);
const doctorName = ref("");
const currentAppointment = ref(null);
const slots = ref([]);

const loadData = async () => {
  loading.value = true;
  errorMsg.value = "";
  try {
    const resAppt = await api.get(`/patient/appointments/${apptId}`);
    currentAppointment.value = resAppt.data;
    doctorId.value = resAppt.data.doctor_id;
    doctorName.value = resAppt.data.doctor_name;

    // slots shown
    const resSlots = await api.get(`/patient/doctors/${doctorId.value}/slots`);
    slots.value = resSlots.data.slots || [];
  } catch (err) {
    console.error(err);
    errorMsg.value =
      err?.response?.data?.msg || "Failed to load reschedule data.";
  } finally {
    loading.value = false;
  }
};

onMounted(loadData);

const chooseSlot = async (slotId) => {
  const ok = window.confirm("Confirm rescheduling to this slot?");
  if (!ok) return;

  try {
    await api.patch(`/patient/appointments/${apptId}/reschedule`, {
      slot_id: slotId,
    });
    alert("Appointment rescheduled successfully.");
    router.push("/patient/dashboard");
  } catch (err) {
    console.error(err);
    alert(err?.response?.data?.msg || "Failed to reschedule appointment.");
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

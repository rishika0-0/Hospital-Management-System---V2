<template>
  <div class="container mt-4">
    <h3 class="mb-3">All Appointments</h3>

    <div v-if="errorMsg" class="alert alert-danger">{{ errorMsg }}</div>

    <div class="d-flex justify-content-between align-items-center mb-3">
      <div class="btn-group">
        <button
          class="btn btn-sm"
          :class="filter === 'upcoming' ? 'btn-primary' : 'btn-outline-primary'"
          @click="changeFilter('upcoming')"
        >
          Upcoming
        </button>
        <button
          class="btn btn-sm"
          :class="filter === 'past' ? 'btn-primary' : 'btn-outline-primary'"
          @click="changeFilter('past')"
        >
          Past
        </button>
      </div>
      <button class="btn btn-sm btn-light" @click="loadAppointments">
        ⟳ Refresh
      </button>
    </div>

    <!-- Appointments tab -->
    <div class="card">
      <div class="card-body table-responsive">
        <table class="table table-striped align-middle">
          <thead>
            <tr>
              <th>Date</th>
              <th>Time</th>
              <th>Doctor</th>
              <th>Patient</th>
              <th>Status</th>
              <th style="width: 220px">Change Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="a in appointments" :key="a.id">
              <td>{{ a.date }}</td>
              <td>{{ a.start_time }} - {{ a.end_time }}</td>
              <td>
                {{ a.doctor_name || "—" }}
                <small class="text-muted d-block">ID: {{ a.doctor_id }}</small>
              </td>
              <td>
                {{ a.patient_name || "—" }}
                <small class="text-muted d-block">ID: {{ a.patient_id }}</small>
              </td>
              <td>
                <span class="badge" :class="badgeClass(a.status)">
                  {{ a.status }}
                </span>
              </td>
              <td>
                <div class="btn-group btn-group-sm">
                  <button
                    class="btn btn-outline-primary"
                    :disabled="a.status === 'Booked'"
                    @click="setStatus(a, 'Booked')"
                  >
                    Booked
                  </button>
                  <button
                    class="btn btn-outline-success"
                    :disabled="a.status === 'Completed'"
                    @click="setStatus(a, 'Completed')"
                  >
                    Completed
                  </button>
                  <button
                    class="btn btn-outline-danger"
                    :disabled="a.status === 'Cancelled'"
                    @click="setStatus(a, 'Cancelled')"
                  >
                    Cancelled
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="appointments.length === 0">
              <td colspan="6" class="text-center text-muted">
                No appointments found for this filter.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "../api/http";

const appointments = ref([]);
const filter = ref("upcoming");
const errorMsg = ref("");

const loadAppointments = async () => {
  errorMsg.value = "";
  try {
    const res = await api.get("/admin/appointments", {
      params: { filter: filter.value },
    });
    appointments.value = res.data.appointments || [];
  } catch (err) {
    console.error(err);
    errorMsg.value = err?.response?.data?.msg || "Failed to load appointments.";
  }
};

onMounted(loadAppointments);

const changeFilter = (val) => {
  if (filter.value === val) return;
  filter.value = val;
  loadAppointments();
};

const badgeClass = (status) => {
  if (status === "Completed") return "bg-success";
  if (status === "Cancelled") return "bg-danger";
  return "bg-secondary";
};

const setStatus = async (appt, newStatus) => {
  try {
    await api.patch(`/admin/appointments/${appt.id}/status`, {
      status: newStatus,
    });
    appt.status = newStatus;
  } catch (err) {
    console.error(err);
    alert(err?.response?.data?.msg || "Failed to update status.");
  }
};
</script>

<style scoped>
.card {
  border-radius: 14px;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.12);
}
</style>

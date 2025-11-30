<template>
  <div class="container-fluid mt-4" v-if="!loading">
    <!-- Top bar -->
    <div class="d-flex justify-content-between align-items-center mb-3 px-3">
      <h3>Admin Dashboard</h3>
      <div>
        <button class="btn btn-outline-primary btn-sm me-2" @click="goDoctors">
          Manage Doctors
        </button>
        <button class="btn btn-outline-primary btn-sm me-2" @click="goPatients">
          Manage Patients
        </button>
        <button class="btn btn-outline-primary btn-sm" @click="goAppointments">
          View Appointments
        </button>
        <button
          class="btn btn-outline-danger btn-sm ms-3"
          @click="handleLogout"
        >
          Logout
        </button>
      </div>
    </div>

    <!-- Error message -->
    <div v-if="errorMsg" class="px-3 mb-3">
      <div class="alert alert-danger mb-0">
        {{ errorMsg }}
      </div>
    </div>

    <!-- Doc/patient tab -->
    <div class="row px-3 mb-4">
      <div class="col-md-4 mb-3">
        <div class="card stat-card p-3">
          <h6 class="text-muted mb-1">Total Doctors</h6>
          <h3 class="mb-0">{{ stats.total_doctors }}</h3>
        </div>
      </div>
      <div class="col-md-4 mb-3">
        <div class="card stat-card p-3">
          <h6 class="text-muted mb-1">Total Patients</h6>
          <h3 class="mb-0">{{ stats.total_patients }}</h3>
        </div>
      </div>
      <div class="col-md-4 mb-3">
        <div class="card stat-card p-3">
          <h6 class="text-muted mb-1">Total Appointments</h6>
          <h3 class="mb-0">{{ stats.total_appointments }}</h3>
        </div>
      </div>
    </div>

    <!-- Upcoming appointments -->
    <div class="row px-3">
      <div class="col-12">
        <div class="card">
          <div
            class="card-header d-flex justify-content-between align-items-center"
          >
            <span>Upcoming Appointments</span>
            <button
              class="btn btn-sm btn-light"
              @click="loadDashboard"
              title="Refresh"
            >
              ⟳ Refresh
            </button>
          </div>
          <div class="card-body table-responsive">
            <table class="table table-striped align-middle">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Time</th>
                  <th>Doctor</th>
                  <th>Patient</th>
                  <th>Status</th>
                  <th>Change Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="a in upcoming" :key="a.id">
                  <td>{{ a.date }}</td>
                  <td>{{ a.start_time }} - {{ a.end_time }}</td>
                  <td>
                    {{ a.doctor_name || "—" }}
                    <small class="text-muted d-block">
                      ID: {{ a.doctor_id }}
                    </small>
                  </td>
                  <td>
                    {{ a.patient_name || "—" }}
                    <small class="text-muted d-block">
                      ID: {{ a.patient_id }}
                    </small>
                  </td>
                  <td>
                    <span class="badge" :class="statusBadgeClass(a.status)">
                      {{ a.status }}
                    </span>
                  </td>
                  <td>
                    <div class="btn-group btn-group-sm">
                      <button
                        class="btn btn-outline-primary"
                        :disabled="a.status === 'Booked'"
                        @click="updateStatus(a.id, 'Booked')"
                      >
                        Booked
                      </button>
                      <button
                        class="btn btn-outline-success"
                        :disabled="a.status === 'Completed'"
                        @click="updateStatus(a.id, 'Completed')"
                      >
                        Completed
                      </button>
                      <button
                        class="btn btn-outline-danger"
                        :disabled="a.status === 'Cancelled'"
                        @click="updateStatus(a.id, 'Cancelled')"
                      >
                        Cancelled
                      </button>
                    </div>
                  </td>
                </tr>
                <tr v-if="upcoming.length === 0">
                  <td colspan="6" class="text-center text-muted">
                    No upcoming appointments.
                  </td>
                </tr>
              </tbody>
            </table>
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
import { useRouter } from "vue-router";
import api from "../api/http";

const router = useRouter();

const loading = ref(true);
const errorMsg = ref("");

const stats = ref({
  total_doctors: 0,
  total_patients: 0,
  total_appointments: 0,
});

const upcoming = ref([]);

const loadDashboard = async () => {
  loading.value = true;
  errorMsg.value = "";
  try {
    const res = await api.get("/admin/dashboard");
    stats.value = {
      total_doctors: res.data.total_doctors,
      total_patients: res.data.total_patients,
      total_appointments: res.data.total_appointments,
    };
    upcoming.value = res.data.upcoming_appointments || [];
  } catch (err) {
    console.error(err);
    errorMsg.value =
      err?.response?.data?.msg || "Failed to load admin dashboard.";
  } finally {
    loading.value = false;
  }
};

onMounted(loadDashboard);

const statusBadgeClass = (status) => {
  if (status === "Completed") return "bg-success";
  if (status === "Cancelled") return "bg-danger";
  return "bg-secondary";
};

const updateStatus = async (id, newStatus) => {
  try {
    await api.patch(`/admin/appointments/${id}/status`, { status: newStatus });
    const target = upcoming.value.find((a) => a.id === id);
    if (target) target.status = newStatus;
  } catch (err) {
    console.error(err);
    alert(err?.response?.data?.msg || "Failed to update status.");
  }
};

const goDoctors = () => {
  router.push("/admin/doctors");
};

const goPatients = () => {
  router.push("/admin/patients");
};

const goAppointments = () => {
  router.push("/admin/appointments");
};

const handleLogout = () => {
  localStorage.removeItem("authToken");
  localStorage.removeItem("userRole");
  router.push("/login");
};
</script>

<style scoped>
h3 {
  font-weight: 600;
  color: #1f2937;
}

.card {
  border-radius: 16px;
  border: 1px solid rgba(148, 163, 184, 0.3);
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.12);
  background-color: #ffffffee;
}

.card-header {
  background: linear-gradient(135deg, #4b88deff, #2757bdff);
  color: #ffffff;
  font-weight: 600;
  border-bottom: none;
}

.stat-card {
  background: linear-gradient(135deg, #f9fafb, #e5e7eb);
}

.table thead th {
  background-color: #f3f4f6;
  border-bottom: 2px solid #e5e7eb;
  color: #111827;
}

.table-striped > tbody > tr:nth-of-type(odd) {
  background-color: #f9fafb;
}
</style>

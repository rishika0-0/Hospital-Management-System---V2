<template>
  <div class="container-fluid mt-4" v-if="!loading">
    <div class="d-flex justify-content-between align-items-center mb-3 px-3">
      <h3>Welcome, {{ doctorName || "Doctor" }}</h3>
      <div>
        <button
          class="btn btn-outline-primary btn-sm me-2"
          @click="openAvailability"
        >
          Manage Availability
        </button>

        <button class="btn btn-outline-danger btn-sm" @click="handleLogout">
          Logout
        </button>
      </div>
    </div>

    <div v-if="errorMsg" class="px-3 mb-3">
      <div class="alert alert-danger mb-0">{{ errorMsg }}</div>
    </div>

    <div class="row px-3">
      <!-- Appt. tab -->
      <div class="col-md-8 mb-4">
        <!-- Today's appointments -->
        <div class="card mb-3">
          <div class="card-header">Today's Appointments</div>
          <div class="card-body table-responsive">
            <table class="table table-striped align-middle">
              <thead>
                <tr>
                  <th>Time</th>
                  <th>Patient</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="a in todayAppointments" :key="a.id">
                  <td>{{ a.start_time }} - {{ a.end_time }}</td>
                  <td>{{ a.patient_name || "—" }}</td>
                  <td>
                    <span :class="['badge', statusBadge(a.status)]">
                      {{ a.status }}
                    </span>
                  </td>
                  <td>
                    <button
                      class="btn btn-sm btn-outline-primary"
                      @click="openAppointment(a.id)"
                    >
                      View / Update
                    </button>
                  </td>
                </tr>
                <tr v-if="todayAppointments.length === 0">
                  <td colspan="4" class="text-center text-muted">
                    No appointments scheduled for today.
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="card">
          <div class="card-header d-flex justify-content-between">
            <span>Upcoming Week</span>
            <button class="btn btn-sm btn-light" @click="loadDashboard">
              ⟳ Refresh
            </button>
          </div>
          <div class="card-body table-responsive">
            <table class="table table-striped align-middle">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Time</th>
                  <th>Patient</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="a in weekAppointments" :key="a.id">
                  <td>{{ a.date }}</td>
                  <td>{{ a.start_time }} - {{ a.end_time }}</td>
                  <td>{{ a.patient_name || "—" }}</td>
                  <td>
                    <span :class="['badge', statusBadge(a.status)]">
                      {{ a.status }}
                    </span>
                  </td>
                  <td>
                    <button
                      class="btn btn-sm btn-outline-primary"
                      @click="openAppointment(a.id)"
                    >
                      View / Update
                    </button>
                  </td>
                </tr>
                <tr v-if="weekAppointments.length === 0">
                  <td colspan="5" class="text-center text-muted">
                    No upcoming appointments in the next 7 days.
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div class="col-md-4 mb-4">
        <!-- Assigned patients -->
        <div class="card mb-3">
          <div class="card-header d-flex justify-content-between">
            <span>Assigned Patients</span>
            <button class="btn btn-sm btn-light" @click="loadPatients">
              ⟳
            </button>
          </div>
          <div class="card-body" v-if="showPatients">
            <ul class="list-group">
              <li
                v-for="p in patients"
                :key="p.id"
                class="list-group-item d-flex justify-content-between align-items-center"
              >
                <div>
                  <div>{{ p.name }}</div>
                  <small class="text-muted"
                    >Contact: {{ p.contact || "—" }}</small
                  >
                </div>
                <button
                  class="btn btn-sm btn-outline-primary"
                  @click="viewPatientHistory(p.id)"
                >
                  History
                </button>
              </li>
              <li
                v-if="patients.length === 0"
                class="list-group-item text-center text-muted"
              >
                No patients assigned yet.
              </li>
            </ul>
          </div>
          <div v-else class="card-body text-muted small">
            Click “Show Patients” on top to view list.
          </div>
        </div>

        <div class="card">
          <div class="card-header">Availability</div>
          <div class="card-body">
            <p v-if="availability">
              Current: <strong>{{ availability }}</strong>
            </p>
            <p v-else class="text-muted">
              No availability string configured yet.
            </p>
            <button
              class="btn btn-sm btn-outline-primary"
              @click="openAvailability"
            >
              Update Availability
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
import { useRouter } from "vue-router";
import api from "../api/http";

const router = useRouter();

const loading = ref(true);
const errorMsg = ref("");

const doctorName = ref("");
const todayAppointments = ref([]);
const weekAppointments = ref([]);
const patients = ref([]);
const availability = ref("");

const showPatients = ref(true);

const loadDashboard = async () => {
  loading.value = true;
  errorMsg.value = "";
  try {
    const res = await api.get("/doctor/dashboard");
    doctorName.value = res.data.doctor_name || "";
    todayAppointments.value = res.data.today || [];
    weekAppointments.value = res.data.week || [];
  } catch (err) {
    console.error(err);
    errorMsg.value =
      err?.response?.data?.msg || "Failed to load doctor dashboard.";
  } finally {
    loading.value = false;
  }
};

const loadPatients = async () => {
  try {
    const res = await api.get("/doctor/patients");
    patients.value = res.data.patients || [];
  } catch (err) {
    console.error(err);
  }
};

const loadAvailability = async () => {
  try {
    const res = await api.get("/doctor/availability");
    availability.value = res.data.availability || "";
  } catch (err) {
    console.error(err);
  }
};

onMounted(async () => {
  await loadDashboard();
  await loadPatients();
  await loadAvailability();
});

const statusBadge = (status) => {
  if (status === "Completed") return "bg-success";
  if (status === "Cancelled") return "bg-danger";
  return "bg-secondary";
};

const openAppointment = (id) => {
  router.push(`/doctor/appointment/${id}`);
};

const viewPatientHistory = (id) => {
  // you have backend: GET /api/doctor/patients/<id>/history
  router.push(`/doctor/patient/${id}/history`);
};

const openAvailability = () => {
  router.push("/doctor/availability");
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
  background: linear-gradient(135deg, #0ea5e9, #0369a1);
  color: #ffffff;
  font-weight: 600;
  border-bottom: none;
}

.table thead th {
  background-color: #eff6ff;
  border-bottom: 2px solid #bfdbfe;
  color: #111827;
}

.table-striped > tbody > tr:nth-of-type(odd) {
  background-color: #f9fafb;
}
</style>

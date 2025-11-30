<template>
  <div class="container-fluid mt-4" v-if="!loading">
    <div class="d-flex justify-content-between align-items-center mb-3 px-3">
      <div>
        <h3 class="mb-0">Welcome, {{ patientInfo?.name || "Patient" }}</h3>
      </div>
      <div>
        <button class="btn btn-outline-primary btn-sm" @click="goProfile">
          My Profile
        </button>
        <button
          class="btn btn-outline-danger btn-sm ms-2"
          @click="handleLogout"
        >
          Logout
        </button>
      </div>
    </div>

    <!-- Error -->
    <div v-if="errorMsg" class="px-3 mb-3">
      <div class="alert alert-danger mb-0">
        {{ errorMsg }}
      </div>
    </div>

    <div class="row px-3">
      <div class="col-md-4 mb-4">
        <!-- Search Doctors -->
        <div class="card mb-3">
          <div class="card-header">Search Doctors</div>
          <div class="card-body">
            <form @submit.prevent="onSearch">
              <div class="mb-2">
                <input
                  type="text"
                  v-model="searchText"
                  class="form-control"
                  placeholder="Search by name or specialization"
                />
              </div>
              <button class="btn btn-primary w-100" type="submit">
                Search
              </button>
            </form>
          </div>
        </div>

        <div class="card">
          <div class="card-header">Available Specializations</div>
          <ul class="list-group list-group-flush">
            <li
              v-for="dept in departments"
              :key="dept.id"
              class="list-group-item d-flex justify-content-between align-items-center"
            >
              {{ dept.name }}
              <button
                class="btn btn-sm btn-outline-secondary"
                @click="viewDoctorsByDept(dept.id)"
              >
                View Doctors
              </button>
            </li>
            <li
              v-if="departments.length === 0"
              class="list-group-item text-muted text-center"
            >
              No departments listed.
            </li>
          </ul>
        </div>
      </div>

      <!-- Appointments -->
      <div class="col-md-8">
        <!-- Upcoming appointments -->
        <div class="card mb-3">
          <div class="card-header">Upcoming Appointments</div>
          <div class="card-body table-responsive">
            <table class="table table-striped align-middle">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Time</th>
                  <th>Doctor</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="a in upcoming" :key="a.id">
                  <td>{{ a.date }}</td>
                  <td>{{ a.start_time }} - {{ a.end_time }}</td>
                  <td>{{ a.doctor_name || "—" }}</td>
                  <td>
                    <span :class="['badge', badgeClass(a.status)]">
                      {{ a.status }}
                    </span>
                  </td>
                  <td>
                    <button
                      class="btn btn-sm btn-outline-primary me-1"
                      @click="goAppointmentDetails(a.id)"
                    >
                      Details
                    </button>

                    <button
                      v-if="a.status === 'Booked'"
                      class="btn btn-sm btn-outline-primary me-1"
                      @click="goReschedule(a.id)"
                    >
                      Reschedule
                    </button>

                    <button
                      v-if="a.status === 'Booked'"
                      class="btn btn-sm btn-outline-danger"
                      @click="cancelAppointment(a.id)"
                    >
                      Cancel
                    </button>
                  </td>
                </tr>
                <tr v-if="upcoming.length === 0">
                  <td colspan="5" class="text-muted text-center">
                    No upcoming appointments.
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Past appointments -->
        <div class="card">
          <div class="card-header">Past Appointments &amp; History</div>
          <div class="card-body table-responsive">
            <table class="table table-bordered align-middle">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Doctor</th>
                  <th>Diagnosis</th>
                  <th>Prescription</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="a in past" :key="a.id">
                  <td>{{ a.date }}</td>
                  <td>{{ a.doctor_name || "—" }}</td>
                  <td>{{ a.diagnosis || "—" }}</td>
                  <td>{{ a.prescription || "—" }}</td>
                </tr>
                <tr v-if="past.length === 0">
                  <td colspan="4" class="text-muted text-center">
                    No past records.
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
const isCached = ref(false);

const patientInfo = ref(null);
const upcoming = ref([]);
const past = ref([]);
const departments = ref([]);

const searchText = ref("");

const loadDashboard = async () => {
  loading.value = true;
  errorMsg.value = "";
  try {
    const res = await api.get("/patient/dashboard");
    const data = res.data;

    isCached.value = !!data.cached;

    patientInfo.value = data.patient || null;
    upcoming.value = data.upcoming || [];
    past.value = data.past || [];
    departments.value = data.departments || [];
  } catch (err) {
    console.error(err);
    errorMsg.value =
      err?.response?.data?.msg || "Failed to load dashboard data.";
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  loadDashboard();
});

const goProfile = () => {
  router.push("/patient/profile");
};

const handleLogout = () => {
  localStorage.removeItem("authToken");
  localStorage.removeItem("userRole");
  router.push("/login");
};

const onSearch = () => {
  if (!searchText.value.trim()) return;
  router.push({
    path: "/patient/doctors",
    query: { q: searchText.value.trim() },
  });
};

const viewDoctorsByDept = (deptId) => {
  router.push({
    path: "/patient/doctors",
    query: { department_id: deptId },
  });
};

const goAppointmentDetails = (id) => {
  router.push(`/patient/appointments/${id}`);
};

const goReschedule = (id) => {
  router.push(`/patient/appointments/${id}/reschedule`);
};

const cancelAppointment = async (id) => {
  const ok = window.confirm("Cancel this appointment?");
  if (!ok) return;

  try {
    await api.patch(`/patient/appointments/${id}/cancel`);
    await loadDashboard();
  } catch (err) {
    console.error(err);
    alert(err?.response?.data?.msg || "Failed to cancel appointment.");
  }
};

const badgeClass = (status) => {
  if (status === "Completed") return "bg-success";
  if (status === "Cancelled") return "bg-danger";
  return "bg-secondary";
};
</script>

<style scoped>
body {
  min-height: 100vh;
  background: linear-gradient(135deg, #ffffff, #feffff);
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI",
    sans-serif;
}

h3 {
  font-weight: 600;
  color: #1f2937;
}

.card {
  border-radius: 16px;
  border: 1px solid rgba(148, 163, 184, 0.3);
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.12);
  overflow: hidden;
  background-color: #ffffffee;
}

.card-header {
  background: linear-gradient(135deg, #4a90e2, #0ea5e9);
  color: #ffffff;
  font-weight: 600;
  border-bottom: none;
}

.form-control {
  border-radius: 999px;
  border: 1px solid #d1d5db;
  font-size: 0.95rem;
}

.form-control:focus {
  border-color: #60a5fa;
  box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.35);
}

.btn-primary {
  background: linear-gradient(135deg, #4f46e5, #0ea5e9);
  border: none;
  border-radius: 999px;
  font-weight: 600;
}

.btn-outline-primary,
.btn-outline-danger {
  border-radius: 999px;
}

.table thead th {
  background-color: #eef2ff;
  border-bottom: 2px solid #c7d2fe;
  color: #1f2937;
}

.table-striped > tbody > tr:nth-of-type(odd) {
  background-color: #f9fafb;
}

.table-bordered > :not(caption) > * > * {
  border-color: #e5e7eb;
}
</style>

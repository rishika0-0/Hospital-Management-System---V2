<template>
  <div class="container mt-4">
    <h3 class="mb-3">Manage Patients</h3>

    <div v-if="errorMsg" class="alert alert-danger">{{ errorMsg }}</div>

    <!-- Searching -->
    <div class="card mb-3">
      <div class="card-header">Search Patients</div>
      <div class="card-body">
        <form @submit.prevent="loadPatients">
          <div class="input-group">
            <input
              v-model="search"
              type="text"
              class="form-control"
              placeholder="Search by name / contact / ID"
            />
            <button type="submit" class="btn btn-primary">Search</button>
          </div>
        </form>
      </div>
    </div>

    <div class="card">
      <div
        class="card-header d-flex justify-content-between align-items-center"
      >
        <span>Patient List</span>
        <button class="btn btn-sm btn-light" @click="loadPatients">
          ⟳ Refresh
        </button>
      </div>
      <div class="card-body table-responsive">
        <table class="table table-striped align-middle">
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Contact</th>
              <th>Status</th>
              <th style="width: 180px">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in patients" :key="p.id">
              <td>{{ p.id }}</td>
              <td>{{ p.name }}</td>
              <td>{{ p.contact || "—" }}</td>
              <td>
                <span
                  class="badge"
                  :class="p.status ? 'bg-success' : 'bg-secondary'"
                >
                  {{ p.status ? "Active" : "Blacklisted" }}
                </span>
              </td>
              <td>
                <div class="btn-group btn-group-sm">
                  <button
                    class="btn btn-outline-warning"
                    @click="togglePatient(p)"
                  >
                    {{ p.status ? "Blacklist" : "Activate" }}
                  </button>
                  <button
                    class="btn btn-outline-danger"
                    @click="removePatient(p)"
                  >
                    Delete
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="patients.length === 0">
              <td colspan="5" class="text-center text-muted">
                No patients found.
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

const patients = ref([]);
const search = ref("");
const errorMsg = ref("");

const loadPatients = async () => {
  errorMsg.value = "";
  try {
    const res = await api.get("/admin/patients", {
      params: { q: search.value || "" },
    });
    patients.value = res.data.patients || [];
  } catch (err) {
    console.error(err);
    errorMsg.value = err?.response?.data?.msg || "Failed to load patients.";
  }
};

onMounted(loadPatients);

const togglePatient = async (p) => {
  if (!confirm("Toggle this patient's active/blacklisted status?")) return;
  try {
    const res = await api.patch(`/admin/patients/${p.id}/toggle`);
    p.status = res.data.status;
  } catch (err) {
    console.error(err);
    alert(err?.response?.data?.msg || "Failed to update status.");
  }
};

const removePatient = async (p) => {
  if (!confirm("Delete this patient permanently?")) return;
  try {
    await api.delete(`/admin/patients/${p.id}`);
    patients.value = patients.value.filter((x) => x.id !== p.id);
  } catch (err) {
    console.error(err);
    alert(err?.response?.data?.msg || "Failed to delete patient.");
  }
};
</script>

<style scoped>
.card {
  border-radius: 14px;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.12);
}
</style>

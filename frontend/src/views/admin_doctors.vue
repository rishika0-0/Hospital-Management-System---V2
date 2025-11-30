<template>
  <div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h3>Manage Doctors</h3>

      <button class="btn btn-primary" @click="toggleForm">
        {{ showForm ? "Close Form" : "Add Doctor" }}
      </button>
    </div>

    <div v-if="errorMsg" class="alert alert-danger">{{ errorMsg }}</div>

    <!-- Doc func -->
    <transition name="slide">
      <div v-if="showForm" class="card shadow-sm p-4 mb-4">
        <h5 class="mb-3">{{ editing ? "Edit Doctor" : "Add New Doctor" }}</h5>

        <form @submit.prevent="submitForm">
          <div class="row">
            <div class="col-md-6 mb-3">
              <label class="form-label">Name</label>
              <input
                v-model="form.name"
                type="text"
                required
                class="form-control"
              />
            </div>

            <div class="col-md-6 mb-3">
              <label class="form-label">Email</label>
              <input
                v-model="form.email"
                type="email"
                required
                class="form-control"
              />
            </div>

            <div class="col-md-6 mb-3">
              <label class="form-label">Password</label>
              <input
                v-model="form.password"
                type="password"
                class="form-control"
                :placeholder="editing ? '(leave blank to keep same)' : ''"
                :required="!editing"
              />
            </div>

            <div class="col-md-6 mb-3">
              <label class="form-label">Department ID</label>
              <input
                v-model="form.department_id"
                type="number"
                required
                class="form-control"
              />
            </div>

            <div class="col-md-6 mb-3">
              <label class="form-label">Contact</label>
              <input v-model="form.contact" type="text" class="form-control" />
            </div>

            <div class="col-md-6 mb-3">
              <label class="form-label">Availability</label>
              <input
                v-model="form.availability"
                type="text"
                class="form-control"
                placeholder="Mon-Fri: 09:00-12:00"
              />
            </div>
          </div>

          <div class="d-flex gap-2">
            <button type="submit" class="btn btn-success">
              {{ editing ? "Update" : "Create" }}
            </button>

            <button type="button" class="btn btn-secondary" @click="closeForm">
              Cancel
            </button>
          </div>
        </form>
      </div>
    </transition>

    <div class="card">
      <div class="card-header">
        <div class="d-flex justify-content-between">
          <span>Doctor List</span>
          <button class="btn btn-sm btn-outline-dark" @click="loadDoctors">
            Refresh
          </button>
        </div>
      </div>

      <div class="card-body table-responsive">
        <table class="table table-striped align-middle">
          <thead>
            <tr>
              <th>Name</th>
              <th>Dept</th>
              <th>Contact</th>
              <th>Status</th>
              <th width="200">Actions</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="d in doctors" :key="d.id">
              <td>{{ d.name }}</td>
              <td>{{ d.department_id }}</td>
              <td>{{ d.contact || "—" }}</td>
              <td>
                <span
                  :class="'badge ' + (d.status ? 'bg-success' : 'bg-secondary')"
                >
                  {{ d.status ? "Active" : "Blacklisted" }}
                </span>
              </td>

              <td>
                <div class="btn-group btn-group-sm">
                  <button
                    class="btn btn-outline-primary"
                    @click="editDoctor(d)"
                  >
                    Edit
                  </button>
                  <button
                    class="btn btn-outline-warning"
                    @click="toggleDoctor(d)"
                  >
                    {{ d.status ? "Blacklist" : "Activate" }}
                  </button>
                  <button
                    class="btn btn-outline-danger"
                    @click="removeDoctor(d)"
                  >
                    Delete
                  </button>
                </div>
              </td>
            </tr>

            <tr v-if="doctors.length === 0">
              <td colspan="5" class="text-center text-muted">
                No doctors found.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue";
import api from "../api/http";

const doctors = ref([]);
const errorMsg = ref("");

const showForm = ref(false);
const editing = ref(false);
const currentId = ref(null);

const form = reactive({
  name: "",
  email: "",
  password: "",
  department_id: "",
  contact: "",
  availability: "",
});

onMounted(() => loadDoctors());

const loadDoctors = async () => {
  try {
    const res = await api.get("/admin/doctors");
    doctors.value = res.data.doctors;
  } catch (err) {
    errorMsg.value = "Failed to load doctors";
  }
};

const toggleForm = () => (showForm.value = !showForm.value);
const closeForm = () => {
  resetForm();
  showForm.value = false;
};

const submitForm = async () => {
  try {
    const payload = { ...form };
    if (!editing.value) await api.post("/admin/doctors", payload);
    else await api.put(`/admin/doctors/${currentId.value}`, payload);

    loadDoctors();
    closeForm();
  } catch (err) {
    console.log(err);
    alert("Error saving doctor");
  }
};

const editDoctor = (d) => {
  showForm.value = true;
  editing.value = true;
  currentId.value = d.id;

  form.name = d.name;
  form.email = d.email || "";
  form.department_id = d.department_id;
  form.password = "";
  form.contact = d.contact || "";
  form.availability = d.availability || "";
};

const resetForm = () => {
  editing.value = false;
  form.name = "";
  form.email = "";
  form.password = "";
  form.department_id = "";
  form.contact = "";
  form.availability = "";
};

const toggleDoctor = async (d) => {
  if (!confirm("Are you sure?")) return;
  const res = await api.patch(`/admin/doctors/${d.id}/toggle`);
  d.status = res.data.status;
};

const removeDoctor = async (d) => {
  if (!confirm("Delete permanently?")) return;
  await api.delete(`/admin/doctors/${d.id}`);
  doctors.value = doctors.value.filter((x) => x.id !== d.id);
};
</script>

<style scoped>
.slide-enter-from,
.slide-leave-to {
  opacity: 0;
  transform: translateY(-12px);
}
.slide-enter-to,
.slide-leave-from {
  opacity: 1;
  transform: translateY(0);
}
.slide-enter-active,
.slide-leave-active {
  transition: 0.25s ease;
}

.card {
  border-radius: 14px;
}
</style>

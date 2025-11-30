<template>
  <div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h3>Find Doctors</h3>
      <button class="btn btn-outline-secondary btn-sm" @click="goBack">
        Back to Dashboard
      </button>
    </div>

    <div v-if="errorMsg" class="alert alert-danger">{{ errorMsg }}</div>

    <!-- Searching -->
    <div class="card mb-3">
      <div class="card-body">
        <form @submit.prevent="doSearch">
          <div class="row g-2 align-items-center">
            <div class="col-md-8">
              <input
                v-model="search"
                type="text"
                class="form-control"
                placeholder="Search by doctor name or specialization"
              />
            </div>
            <div class="col-md-4 d-flex gap-2">
              <button type="submit" class="btn btn-primary w-50">Search</button>
              <button
                type="button"
                class="btn btn-outline-secondary w-50"
                @click="clearSearch"
              >
                Clear
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>

    <!--list of doc-->
    <div class="row mt-2">
      <div class="col-md-4 mb-3" v-for="d in doctors" :key="d.id">
        <div class="card h-100">
          <div class="card-body d-flex flex-column">
            <h5 class="card-title mb-1">{{ d.name }}</h5>
            <p class="card-subtitle mb-2 text-muted">
              {{ d.department || "No department" }}
            </p>
            <p class="mb-1"><strong>Contact:</strong> {{ d.contact || "—" }}</p>
            <p class="mb-2">
              <strong>Availability:</strong>
              <span class="text-muted">{{
                d.availability || "Not specified"
              }}</span>
            </p>
            <p class="mb-3">
              <span
                class="badge"
                :class="d.status ? 'bg-success' : 'bg-secondary'"
              >
                {{ d.status ? "Active" : "Inactive" }}
              </span>
            </p>

            <button
              class="btn btn-outline-primary mt-auto"
              :disabled="!d.status"
              @click="viewSlots(d.id)"
            >
              View Slots &amp; Book
            </button>
          </div>
        </div>
      </div>

      <div
        v-if="!loading && doctors.length === 0"
        class="text-center text-muted"
      >
        No doctors found for this search.
      </div>
    </div>

    <div
      v-if="loading"
      class="d-flex justify-content-center align-items-center mt-4"
    >
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import api from "../api/http";

const router = useRouter();
const route = useRoute();

const doctors = ref([]);
const search = ref(route.query.q || "");
const loading = ref(false);
const errorMsg = ref("");

const currentDept = ref(route.query.department_id || "");

const loadDoctors = async () => {
  loading.value = true;
  errorMsg.value = "";
  try {
    const res = await api.get("/patient/doctors", {
      params: {
        q: search.value || "",
        department_id: currentDept.value || "",
      },
    });
    doctors.value = res.data.doctors || [];
  } catch (err) {
    console.error(err);
    errorMsg.value = err?.response?.data?.msg || "Failed to load doctors list.";
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  loadDoctors();
});

const doSearch = () => {
  router.push({
    path: "/patient/doctors",
    query: {
      q: search.value || "",
      department_id: currentDept.value || "",
    },
  });
  loadDoctors();
};

const clearSearch = () => {
  search.value = "";
  currentDept.value = "";
  router.push({ path: "/patient/doctors" });
  loadDoctors();
};

const viewSlots = (id) => {
  router.push(`/patient/doctors/${id}/book`);
};

const goBack = () => {
  router.push("/patient/dashboard");
};
</script>

<style scoped>
.card {
  border-radius: 14px;
  box-shadow: 0 8px 20px rgba(15, 23, 42, 0.08);
}
</style>

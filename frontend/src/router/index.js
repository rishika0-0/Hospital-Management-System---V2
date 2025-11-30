import { createRouter, createWebHistory } from "vue-router";
import { useAuth } from "../stores/auth";

import Login from "../views/login.vue";
import Register from "../views/register.vue";

import DoctorDashboard from "../views/doctor_dashboard.vue";
import DoctorAppointment from "../views/doctor_appointment.vue";
import DoctorAvailability from "../views/doctor_availability.vue";
import DoctorPatientHistory from "../views/doctor_patient_history.vue";

import PatientDashboard from "../views/patient_dashboard.vue";
import PatientDoctors from "../views/patient_doctor.vue";
import PatientBookAppointment from "../views/patient_books_appointment.vue";
import PatientAppointment from "../views/patient_appointment_detail.vue";
import PatientReschedule from "../views/patient_reschedule_appointment.vue";
import PatientProfile from "../views/patient_profile.vue";

import AdminDashboard from "../views/admin_dashboard.vue";
import AdminDoctors from "../views/admin_doctors.vue";
import AdminPatients from "../views/admin_patients.vue";
import AdminAppointments from "../views/admin_appointments.vue";

const routes = [
  { path: "/", redirect: "/login" },
  { path: "/login", component: Login },
  { path: "/register", component: Register },
  { path: "/admin/dashboard", component: AdminDashboard },
  { path: "/admin/doctors", component: AdminDoctors },
  { path: "/admin/patients", component: AdminPatients },
  { path: "/admin/appointments", component: AdminAppointments },
  { path: "/doctor/dashboard", component: DoctorDashboard },
  { path: "/doctor/appointment/:id", component: DoctorAppointment, props: true },
  { path: "/doctor/availability", component: DoctorAvailability },
  { path: "/doctor/patient/:id/history", component: DoctorPatientHistory, props: true,},
  { path: "/patient/dashboard", component: PatientDashboard },
  { path: "/patient/doctors", component: PatientDoctors },
  { path: "/patient/doctors/:id/book", component: PatientBookAppointment, props: true,},  
  { path: "/patient/appointments/:id", component: PatientAppointment, props: true },
  { path: "/patient/appointments/:id/reschedule",component: PatientReschedule, props: true,}, 
  { path: "/patient/profile", component: PatientProfile },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem("authToken");
  if (!token && to.path !== "/login" && to.path !== "/register") {
    return next("/login");
  }

  
  next();
});

export default router;

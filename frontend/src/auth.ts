import { ref } from "vue";

const authenticated = ref(false);
const employee = ref(localStorage.getItem("isEmployee") === "true");

export function setAuthenticated(value: boolean) {
  authenticated.value = value;
}

export function hasAuthenticatedSession() {
  return authenticated.value;
}

export function setEmployee(value: boolean) {
  employee.value = value;
  if (value) {
    localStorage.setItem("isEmployee", "true");
  } else {
    localStorage.setItem("isEmployee", "false");
  }
}

export function isEmployeeUser() {
  return employee.value;
}

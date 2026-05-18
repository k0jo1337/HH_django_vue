import { ref } from "vue";

const authenticated = ref(false);
const employee = ref(false);

export function setAuthenticated(value: boolean) {
  authenticated.value = value;
}

export function hasAuthenticatedSession() {
  return authenticated.value;
}

export function setEmployee(value: boolean) {
  employee.value = value;
  if (value) {
    localStorage.setItem('isEmployee', 'true');
  } else {
    localStorage.setItem('isEmployee', 'false');
  }
}

export function isEmployeeUser() {
  const stored = localStorage.getItem('isEmployee');
  if (stored !== null) {
    return stored === 'true';
  }
  return employee.value;
}
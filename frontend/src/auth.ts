import { ref } from "vue";

const authenticated = ref(false);

export function setAuthenticated(value: boolean) {
  authenticated.value = value;
}

export function hasAuthenticatedSession() {
  return authenticated.value;
}

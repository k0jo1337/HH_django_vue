<script setup>
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
import api from "../api";
import { setAuthenticated } from "../auth";
import FormField from "../components/FormField.vue";

const router = useRouter();

const form = reactive({
  username: "",
  password: "",
});

const error = ref("");
const success = ref("");
const loading = ref(false);

const loginFields = [
  { name: "username", label: "Логин:", type: "text", required: true, autocomplete: "username" },
  { name: "password", label: "Пароль:", type: "password", required: true, autocomplete: "current-password" },
];

async function loginUser() {
  error.value = "";
  success.value = "";

  try {
    loading.value = true;

    const response = await api.post(
      "/account/login/",
      {
        username: form.username,
        password: form.password,
      }
    );

    success.value = response.data.message;
    setAuthenticated(true);

    await router.push("/home");

  } catch (err) {
    if (err.response?.data?.error) {
      error.value = err.response.data.error;
    } else {
      error.value = "Ошибка сервера";
    }
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <main class="main">

    <div class="parent_form">

      <div class="form_logo">
        <img class="form-logo-full" src="/Hostel_logo.png" alt="Hostel Helper">
        <img class="form-logo-compact" src="/Hostel_logo.png" alt="Hostel Helper">
      </div>

      <div class="adaptiv_form">

        <div class="input_form">
          <h1>Авторизация</h1>
        </div>

        <hr>

        <form @submit.prevent="loginUser">

          <FormField
            v-for="field in loginFields"
            :key="field.name"
            v-model="form[field.name]"
            :field="field"
          />

          <div class="input_form">
            <input
              type="submit"
              :value="loading ? 'Вход...' : 'Авторизоваться'"
              class="btn-primary"
              :disabled="loading"
            >
          </div>

        </form>

        <div
          v-if="success"
          class="alert alert-success mt-3"
        >
          {{ success }}
        </div>

        <div
          v-if="error"
          class="alert alert-danger mt-3"
        >
          {{ error }}
        </div>

        <h6>
          Нет аккаунта?

          <RouterLink to="/registration">
            Регистрация
          </RouterLink>
        </h6>

      </div>

    </div>

    <div class="parent_entrance">

      <div class="adaptiv_entrance">
        <img
          src="/entrance_img.png"
          alt="image"
        >
      </div>

    </div>

  </main>
</template>
